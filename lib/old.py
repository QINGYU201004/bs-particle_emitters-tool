import json
import os

DEFAULT_CURVE = {
    "x1": 0.333333343,
    "y1": 0.333333343,
    "x2": 0.666666687,
    "y2": 0.666666687,
}


def normalize_value(value):
    if isinstance(value, list) and len(value) == 3:
        return {"x": value[0], "y": value[1], "z": value[2]}
    return value


def wrap_curve(value):
    """Convert fixed-format scalars/vectors/curve arrays into the old curve object."""
    base = dict(DEFAULT_CURVE)

    if isinstance(value, dict) and {"x1", "y1", "x2", "y2", "from", "to"} <= set(value.keys()):
        return {
            "x1": value["x1"],
            "y1": value["y1"],
            "x2": value["x2"],
            "y2": value["y2"],
            "from": normalize_value(value["from"]),
            "to": normalize_value(value["to"]),
        }

    if isinstance(value, list):
        if len(value) == 6:
            return {
                "x1": value[0],
                "y1": value[1],
                "x2": value[2],
                "y2": value[3],
                "from": normalize_value(value[4]),
                "to": normalize_value(value[5]),
            }
        if len(value) == 3:
            vec = normalize_value(value)
            base["from"] = vec
            base["to"] = dict(vec)
            return base
        if len(value) == 2:
            base["from"] = normalize_value(value[0])
            base["to"] = normalize_value(value[1])
            return base

    base["from"] = normalize_value(value)
    base["to"] = normalize_value(value)
    return base


def drop_zero_vector(value):
    if not isinstance(value, dict):
        return {}
    return {k: v for k, v in value.items() if v != 0}


def add_if_present(dst, key, value, *, keep_zero=False):
    if value is None:
        return
    if not keep_zero and value in ({}, [], ""):
        return
    dst[key] = value


def is_default_curve(value):
    if not isinstance(value, dict):
        return False
    return value == {**DEFAULT_CURVE, "from": 0.0, "to": 0.0}


def is_meaningful_planar(planar):
    if planar.get("randomAngle") is True:
        return True
    for key, value in planar.items():
        if key == "__class":
            continue
        if isinstance(value, dict) and not is_default_curve(value):
            return True
        if value not in (0, 0.0, False, None):
            return True
    return False


def convert_spawn_rate(component, emitter):
    duration = component.get("duration")
    if duration not in (None, 0):
        emitter["emitterDuration"] = duration

    add_if_present(emitter, "spawnRate", wrap_curve(component.get("spawnRate")))

    if "spawnRateJitter" in component:
        add_if_present(emitter, "spawnRateJitter", wrap_curve(component.get("spawnRateJitter")))


def convert_spawn_burst(component, emitter):
    bursts = component.get("bursts")
    if bursts:
        emitter["bursts"] = bursts


def convert_spawn_planar(component, emitter, components):
    planar = {"__class": "SpawnPlanar"}

    if component.get("randomAngle") is True:
        planar["randomAngle"] = True

    for key in ("minAngle", "maxAngle", "minSpeedXY", "maxSpeedXY", "minSpeedZ", "maxSpeedZ"):
        if key in component:
            planar[key] = wrap_curve(component[key])

    if "spawnMaxSize" in component:
        emitter["spawnMaxSize"] = wrap_curve(component["spawnMaxSize"])
    if "spawnMinSize" in component and component["spawnMinSize"] != 0:
        emitter["spawnMinSize"] = wrap_curve(component["spawnMinSize"])

    if is_meaningful_planar(planar):
        components.append(planar)


def convert_spawn_location(component, emitter):
    if "spawnShape" in component:
        emitter["spawnShape"] = component["spawnShape"]
    if "spawnMaxSize" in component:
        emitter["spawnMaxSize"] = wrap_curve(component["spawnMaxSize"])
    if "spawnMinSize" in component and component["spawnMinSize"] != 0:
        emitter["spawnMinSize"] = wrap_curve(component["spawnMinSize"])


def convert_spawn_cone(component, components):
    cone = {"__class": "SpawnCone"}

    if "direction" in component:
        cone["direction"] = wrap_curve(component["direction"])
    if "directionJitterAngle" in component:
        cone["directionJitterAngle"] = wrap_curve(component["directionJitterAngle"])
    if "velocity" in component and component["velocity"] != 0:
        cone["velocity"] = wrap_curve(component["velocity"])
    if "velocityJitter" in component and component["velocityJitter"] != 0:
        cone["velocityJitter"] = wrap_curve(component["velocityJitter"])

    if len(cone) > 1:
        components.append(cone)


def convert_spawn_velocity(component, components):
    velocity_comp = {"__class": "SpawnVelocityComponent"}

    if "velocity" in component:
        velocity_comp["velocity"] = wrap_curve(component["velocity"])
    if "velocityJitter" in component:
        velocity_comp["velocityJitter"] = wrap_curve(component["velocityJitter"])

    components.append(velocity_comp)


def convert_deceleration(component, components):
    components.append({
        "__class": "Deceleration",
        "deceleration": wrap_curve(component.get("deceleration", [0, 0, 0])),
    })


def convert_ground(component, components):
    ground = {"__class": component.get("__class", "Ground")}
    if component.get("__class") == "Ground":
        if "bounciness" in component:
            ground["bounciness"] = wrap_curve(component["bounciness"])
        if "friction" in component:
            ground["friction"] = wrap_curve(component["friction"])
    components.append(ground)


def convert_curl_noise(component, components):
    curl = {"__class": "CurlNoise"}
    if "frequency" in component:
        curl["frequency"] = wrap_curve(component["frequency"])
    if "strength" in component:
        curl["strength"] = wrap_curve(component["strength"])
    components.append(curl)


def convert_component(component, emitter, components):
    cls = component.get("__class")

    if cls == "SpawnRate":
        convert_spawn_rate(component, emitter)
    elif cls == "SpawnBurst":
        convert_spawn_burst(component, emitter)
    elif cls == "SpawnPlanar":
        convert_spawn_planar(component, emitter, components)
    elif cls == "SpawnLocation":
        convert_spawn_location(component, emitter)
    elif cls == "SpawnCone":
        convert_spawn_cone(component, components)
    elif cls == "SpawnVelocityComponent":
        convert_spawn_velocity(component, components)
    elif cls == "Deceleration":
        convert_deceleration(component, components)
    elif cls in {"Ground", "SimpleGround"}:
        convert_ground(component, components)
    elif cls == "CurlNoise":
        convert_curl_noise(component, components)


def convert_render(render):
    old_render = {}

    ordered_keys = (
        "globalScale",
        "scale",
        "scaleJitter",
        "color",
        "alpha",
        "gradient",
        "angle",
        "angleJitter",
        "rotationSpeed",
        "rotationSpeedJitter",
        "orientToDirection",
        "loopMovieClip",
        "alphaFadeout",
        "tailLength",
        "tailLengthJitter",
        "trailEnabled",
        "trailDuration",
        "trailWidth",
    )

    for key in ordered_keys:
        if key not in render:
            continue
        value = render[key]

        if key in {"globalScale", "alphaFadeout", "trailEnabled", "orientToDirection", "loopMovieClip"}:
            old_render[key] = value
        else:
            old_render[key] = wrap_curve(value)

    return old_render


def convert_effect(effect):
    new_emitter = effect.get("emitter", {})
    old_emitter = {
        "maxParticleCount": int(new_emitter.get("maxParticleCount", 1)),
        "mass": new_emitter.get("mass", 1.0),
        "spawnPointOffset": drop_zero_vector(new_emitter.get("spawnPointOffset", {})),
        "gravity": wrap_curve(new_emitter.get("gravity", [0, 0, 0])),
    }

    if new_emitter.get("emitterDelay") not in (None, 0):
        old_emitter["emitterDelay"] = new_emitter["emitterDelay"]

    if "lifetime" in new_emitter:
        old_emitter["lifetime"] = wrap_curve(new_emitter["lifetime"])
    if "lifetimeJitter" in new_emitter and new_emitter["lifetimeJitter"] != 0:
        old_emitter["lifetimeJitter"] = wrap_curve(new_emitter["lifetimeJitter"])

    old_emitter["bursts"] = []
    old_components = []

    for component in new_emitter.get("components", []):
        convert_component(component, old_emitter, old_components)

    return {
        "emitter": old_emitter,
        "render": convert_render(effect.get("render", {})),
        "movieclip": effect.get("movieclip", []),
        "components": old_components,
    }


def convert_to_old_final(new_data):
    return {key: convert_effect(effect) for key, effect in new_data.items()}


def convert_file_to_old(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    result = convert_to_old_final(data)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    return result


if __name__ == "__main__":
    input_file = 'particle_emitters_fixed.json'
    output_file = 'particle_emitters_old.json'

    if os.path.exists(input_file):
        convert_file_to_old(input_file, output_file)
        print('直接运行脚本：转换成功')
    else:
        print(f'文件不存在: {input_file}')
