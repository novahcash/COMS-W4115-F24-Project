import json
import os
import sys

DEFAULT_ATTR_VAL = 1
DEFAULT_SPRITE_IDLE = "sprite_default"
DEFAULT_AI_SCRIPT = "behavior_default"

DEFAULT_ATTACK = {
    "damage_type": "physical",
    "target_type": "single",
    "damage_mod": 1.0,
    "mod_type": "additive",
    "effect": "",
    "effect_chance": 0.0
}

ALL_ATTRS = ["hp", "p_attack", "m_attack", "p_defense", "m_defense", "speed", "level", "exp"]

VALID_DAMAGE_TYPES = {"physical", "magical"}
VALID_TARGET_TYPES = {"single", "multi", "row", "all"}
VALID_MOD_TYPES = {"additive", "multiplicative"}

class Generator:
    def __init__(self, ast_data):
        self.ast_data = ast_data
        self.entity_name = None
        self.entity_name_str = None
        self.entity_data = None
        self.class_name = None
        self.attributes = {}
        self.sprites = None
        self.ai_script = DEFAULT_AI_SCRIPT
        self.basic_attack = {}
        self.additional_attacks = {}

    def snake_to_pascal(self, name):
        return ''.join(word.capitalize() for word in name.split('_'))

    def parse_ast_value(self, node):
        vtype = node.get("type")
        vval = node.get("value")

        if vtype == "INTEGER":
            return int(vval)
        elif vtype == "FLOAT":
            return float(vval)
        elif vtype == "STRING":
            return vval
        else:
            if vtype in ("KEY", "IDENTIFIER"):
                return vval
            raise ValueError(f"Unexpected value type '{vtype}' in AST.")
    
    def type_check_attrs(self, attributes):
        for attr in ALL_ATTRS:
            val = attributes.get(attr, DEFAULT_ATTR_VAL)
            if not isinstance(val, int):
                raise ValueError(f"Type error: Attribute '{attr}' should be an integer, got {type(val).__name__}.")
        return attributes
    
    def type_check_sprites(self, sprites):
        sprite_idle = sprites.get("idle", DEFAULT_SPRITE_IDLE)
        if not isinstance(sprite_idle, str):
            raise ValueError("Type error: sprite_idle must be a string.")
        for k, v in sprites.items():
            if not isinstance(v, str):
                raise ValueError(f"Type error: Sprite '{k}' should be a string, got {type(v).__name__}.")
        return sprites
    
    def type_check_ai_script(self, ai_script):
        if not isinstance(ai_script, str):
            raise ValueError(f"Type error: AI script must be a string, got {type(ai_script).__name__}.")
        return ai_script
    
    def fill_attack_defaults(self, attack_dict):
        filled = dict(DEFAULT_ATTACK)

        if "target" in attack_dict:
            if not isinstance(attack_dict["target"], str):
                raise ValueError(f"Type error: Attack target must be string, got {type(attack_dict['target']).__name__}.")
            filled["target_type"] = attack_dict["target"]
        if "modifier" in attack_dict:
            mod_val = attack_dict["modifier"]
            if isinstance(mod_val, int):
                mod_val = float(mod_val)
            if not isinstance(mod_val, float):
                raise ValueError(f"Type error: Attack modifier must be float, got {type(mod_val).__name__}.")
            filled["damage_mod"] = mod_val
        if "mod_type" in attack_dict:
            if not isinstance(attack_dict["mod_type"], str):
                raise ValueError(f"Type error: Attack mod_type must be string, got {type(attack_dict['mod_type']).__name__}.")
            filled["mod_type"] = attack_dict["mod_type"]
        if "effect" in attack_dict:
            eff_val = attack_dict["effect"]
            if not isinstance(eff_val, str):
                raise ValueError(f"Type error: Attack effect must be string, got {type(eff_val).__name__}.")
            filled["effect"] = eff_val
        if "effect_chance" in attack_dict:
            eff_chance = attack_dict["effect_chance"]
            if isinstance(eff_chance, int):
                eff_chance = float(eff_chance)
            if not isinstance(eff_chance, float):
                raise ValueError(f"Type error: Attack effect_chance must be float, got {type(eff_chance).__name__}.")
            filled["effect_chance"] = eff_chance

        if not isinstance(filled["target_type"], str):
            raise ValueError(f"Type error: Attack target_type must be string.")
        if not isinstance(filled["damage_mod"], float):
            raise ValueError(f"Type error: Attack damage_mod must be float.")
        if not isinstance(filled["mod_type"], str):
            raise ValueError(f"Type error: Attack mod_type must be string.")
        if not isinstance(filled["effect"], str):
            raise ValueError("Type error: Attack effect must be string.")
        if not isinstance(filled["effect_chance"], float):
            raise ValueError("Type error: Attack effect_chance must be float.")
    
        if filled["damage_type"] not in VALID_DAMAGE_TYPES:
            raise ValueError(f"Invalid damage_type: '{filled['damage_type']}'. Valid types: {VALID_DAMAGE_TYPES}")
        if filled["target_type"] not in VALID_TARGET_TYPES:
            raise ValueError(f"Invalid target_type: '{filled['target_type']}'. Valid types: {VALID_TARGET_TYPES}")
        if filled["mod_type"] not in VALID_MOD_TYPES:
            raise ValueError(f"Invalid mod_type: '{filled['mod_type']}'. Valid types: {VALID_MOD_TYPES}")
        if filled["damage_mod"] < 0:
            raise ValueError(f"Invalid damage_mod: {filled['damage_mod']}. Must be >= 0.")
        if filled["effect_chance"] < 0.0 or filled["effect_chance"] > 1.0:
            raise ValueError(f"Invalid effect_chance: {filled['effect_chance']}. Must be between 0 and 1, inclusive.")
        
        return filled
    
    def process_ast(self):
        data = self.ast_data
        if "body" not in data or not data["body"]:
            raise ValueError("No entities found in AST.")

        first_entry = data["body"][0]
        if first_entry["type"] != "ENTRY":
            raise ValueError("Expected ENTRY as the first element in AST body.")

        self.entity_name = first_entry["key"]["value"]
        self.class_name = self.snake_to_pascal(self.entity_name)

        entity_data = {}
        for item in first_entry["value"]:
            if item["type"] == "ENTRY":
                key_name = item["key"]["value"]
                val_node = item["value"]
                entity_data[key_name] = val_node

        self.entity_data = entity_data

        if "name" not in self.entity_data:
            raise ValueError(f"Required 'name' not found for entity '{self.entity_name}'.")

        name_node = self.entity_data["name"]
        self.entity_name_str = self.parse_ast_value(name_node)
        if not isinstance(self.entity_name_str, str):
            raise ValueError("'name' must be a string.")

        attributes = self.entity_data.get("attributes", {})
        if isinstance(attributes, list):
            attr_dict = {}
            for it in attributes:
                if it["type"] == "ENTRY":
                    attr_key = it["key"]["value"]
                    attr_val_node = it["value"]
                    attr_val = self.parse_ast_value(attr_val_node)
                    attr_dict[attr_key] = attr_val
            attributes = attr_dict

        attributes = self.type_check_attrs(attributes)
        for attr in ALL_ATTRS:
            if attr not in attributes:
                attributes[attr] = DEFAULT_ATTR_VAL
        self.attributes = attributes

        sprites = self.entity_data.get("sprites", {})
        if isinstance(sprites, list):
            spr_dict = {}
            for it in sprites:
                if it["type"] == "ENTRY":
                    spr_key = it["key"]["value"]
                    spr_val_node = it["value"]
                    spr_val = self.parse_ast_value(spr_val_node)
                    spr_dict[spr_key] = spr_val
            sprites = spr_dict
        else:
            if isinstance(sprites, list):
                pass
            else:
                new_spr = {}
                for k, node_val in sprites.items():
                    new_spr[k] = self.parse_ast_value(node_val)
                sprites = new_spr

        sprites = self.type_check_sprites(sprites)
        self.sprites = sprites

        behavior = self.entity_data.get("behavior", {})
        if isinstance(behavior, list):
            beh_dict = {}
            for it in behavior:
                if it["type"] == "ENTRY":
                    key_val = it["key"]["value"]
                    val = it["value"]
                    if key_val == "attacks":
                        attacks_val = {}
                        for a in val:
                            if a["type"] == "ENTRY":
                                att_key = a["key"]["value"]
                                att_val_block = a["value"]
                                att_dict = {}
                                for sub in att_val_block:
                                    if sub["type"] == "ENTRY":
                                        attack_prop_key = sub["key"]["value"]
                                        attack_prop_val_node = sub["value"]
                                        attack_prop_val = self.parse_ast_value(attack_prop_val_node)
                                        att_dict[attack_prop_key] = attack_prop_val
                                attacks_val[att_key] = att_dict
                        beh_dict["attacks"] = attacks_val
                    else:
                        if isinstance(val, dict) and "type" in val:
                            beh_dict[key_val] = self.parse_ast_value(val)
                        else:
                            beh_dict[key_val] = val
            behavior = beh_dict
        else:
            new_beh = {}
            for k, node_val in behavior.items():
                if k == "attacks":
                    pass
                else:
                    new_beh[k] = self.parse_ast_value(node_val)
            behavior = new_beh

        ai_script = behavior.get("ai_script", DEFAULT_AI_SCRIPT)
        ai_script = self.type_check_ai_script(ai_script)
        self.ai_script = ai_script

        attacks = behavior.get("attacks", {})
        basic_attack = attacks.get("basic", {})
        self.basic_attack = self.fill_attack_defaults(basic_attack)

        additional_attacks = {}
        for atk_name, atk_value in attacks.items():
            if atk_name == "basic":
                continue
            additional_attacks[atk_name] = self.fill_attack_defaults(atk_value)
        self.additional_attacks = additional_attacks

    def generate_cpp(self, output_file="output.cpp"):
        cpp_lines = []

        cpp_lines.append("#include <iostream>")
        cpp_lines.append("#include <vector>")
        cpp_lines.append("#include <string>")
        cpp_lines.append("#include <utility>")
        cpp_lines.append("")
        cpp_lines.append("using namespace std;")
        cpp_lines.append("")

        cpp_lines.append("struct AttackInfo {")
        cpp_lines.append("    string damage_type;")
        cpp_lines.append("    string target_type;")
        cpp_lines.append("    float damage_mod;")
        cpp_lines.append("    string mod_type;")
        cpp_lines.append("    string effect;")
        cpp_lines.append("    float effect_chance;")
        cpp_lines.append("};")
        cpp_lines.append("")

        cpp_lines.append(f"class {self.class_name} {{")
        cpp_lines.append("public:")

        for attr in ALL_ATTRS:
            cpp_lines.append(f"    int {attr} = {self.attributes[attr]};")

        cpp_lines.append(f'    string entity_name_str = "{self.entity_name_str}";')

        sprite_idle = self.sprites.get("idle", DEFAULT_SPRITE_IDLE)
        cpp_lines.append(f'    string sprite_idle = "{sprite_idle}";')

        for k, v in self.sprites.items():
            if k != "idle":
                cpp_lines.append(f'    string sprite_{k} = "{v}";')

        cpp_lines.append(f'    string ai_script = "{self.ai_script}";')

        cpp_lines.append("\nprivate:")
        cpp_lines.append("    vector<pair<string,string>> sprites_data;")
        cpp_lines.append("    vector<pair<string, AttackInfo>> attacks_data;")

        cpp_lines.append("\npublic:")

        cpp_lines.append(f"    {self.class_name}() {{")
        cpp_lines.append("        // Initialize sprites")
        cpp_lines.append('        sprites_data.emplace_back("idle", sprite_idle);')
        for k, v in self.sprites.items():
            if k != "idle":
                cpp_lines.append(f'        sprites_data.emplace_back("{k}", sprite_{k});')
        cpp_lines.append("\n        // Initialize attacks")
        for atk_name, atk_data in self.additional_attacks.items():
            cpp_lines.append("        {")
            cpp_lines.append("            AttackInfo info;")
            cpp_lines.append(f'            info.damage_type = "{atk_data["damage_type"]}";')
            cpp_lines.append(f'            info.target_type = "{atk_data["target_type"]}";')
            cpp_lines.append(f'            info.damage_mod = {atk_data["damage_mod"]}f;')
            cpp_lines.append(f'            info.mod_type = "{atk_data["mod_type"]}";')
            cpp_lines.append(f'            info.effect = "{atk_data["effect"]}";')
            cpp_lines.append(f'            info.effect_chance = {atk_data["effect_chance"]}f;')
            cpp_lines.append(f'            attacks_data.emplace_back("{atk_name}", info);')
            cpp_lines.append("        }")
        cpp_lines.append("        {")
        cpp_lines.append("            AttackInfo info;")
        cpp_lines.append(f'            info.damage_type = "{self.basic_attack["damage_type"]}";')
        cpp_lines.append(f'            info.target_type = "{self.basic_attack["target_type"]}";')
        cpp_lines.append(f'            info.damage_mod = {self.basic_attack["damage_mod"]}f;')
        cpp_lines.append(f'            info.mod_type = "{self.basic_attack["mod_type"]}";')
        cpp_lines.append(f'            info.effect = "{self.basic_attack["effect"]}";')
        cpp_lines.append(f'            info.effect_chance = {self.basic_attack["effect_chance"]}f;')
        cpp_lines.append('            attacks_data.emplace_back("basic", info);')
        cpp_lines.append("        }")
        cpp_lines.append("    }")

        for attr in ALL_ATTRS:
            cpp_lines.append(f"    int get_{attr}() const {{ return {attr}; }}")

        cpp_lines.append("    string get_entity_name() const { return entity_name_str; }")

        cpp_lines.append("    string get_ai_script() const { return ai_script; }")

        cpp_lines.append("\n    int deal_damage(string damage_type, string target_type, int damage, float damage_mod, string mod_type, string effect, float effect_chance) {")
        cpp_lines.append("        // Placeholder implementation.")
        cpp_lines.append("        return 0;")
        cpp_lines.append("    }")

        cpp_lines.append("\n    vector<pair<string,string>> get_all_sprites() const {")
        cpp_lines.append("        return sprites_data;")
        cpp_lines.append("    }")

        cpp_lines.append("\n    vector<string> get_all_attack_names() const {")
        cpp_lines.append("        vector<string> names;")
        cpp_lines.append("        for (const auto &p : attacks_data) {")
        cpp_lines.append("            names.push_back(p.first);")
        cpp_lines.append("        }")
        cpp_lines.append("        return names;")
        cpp_lines.append("    }")

        cpp_lines.append("\n    AttackInfo get_attack_info(const string &attack_name) const {")
        cpp_lines.append("        for (const auto &p : attacks_data) {")
        cpp_lines.append("            if (p.first == attack_name) return p.second;")
        cpp_lines.append("        }")
        cpp_lines.append("        // Return default AttackInfo if not found")
        cpp_lines.append("        AttackInfo empty_info;")
        cpp_lines.append('        empty_info.damage_type = "physical";')
        cpp_lines.append('        empty_info.target_type = "single";')
        cpp_lines.append('        empty_info.damage_mod = 1.0f;')
        cpp_lines.append('        empty_info.mod_type = "additive";')
        cpp_lines.append('        empty_info.effect = "";')
        cpp_lines.append('        empty_info.effect_chance = 0.0f;')
        cpp_lines.append("        return empty_info;")
        cpp_lines.append("    }")

        cpp_lines.append("\n    int basic_attack() {")
        cpp_lines.append('        AttackInfo info = get_attack_info("basic");')
        cpp_lines.append('        int damage = (info.damage_type == "physical") ? p_attack : m_attack;')
        cpp_lines.append("        return deal_damage(info.damage_type, info.target_type, damage, info.damage_mod, info.mod_type, info.effect, info.effect_chance);")
        cpp_lines.append("    }")

        for atk_name in self.additional_attacks.keys():
            cpp_lines.append(f"\n    int {atk_name}_attack() {{")
            cpp_lines.append(f'        AttackInfo info = get_attack_info("{atk_name}");')
            cpp_lines.append('        int damage = (info.damage_type == "physical") ? p_attack : m_attack;')
            cpp_lines.append("        return deal_damage(info.damage_type, info.target_type, damage, info.damage_mod, info.mod_type, info.effect, info.effect_chance);")
            cpp_lines.append("    }")

        cpp_lines.append("};")
        cpp_lines.append("")

        cpp_lines.append("int main() {")
        cpp_lines.append(f"    {self.class_name} entity;")
        cpp_lines.append("")
        cpp_lines.append(f'    cout << "{self.class_name}:" << endl;')
        cpp_lines.append('    cout << "  name: \\"" << entity.get_entity_name() << "\\"" << endl;')
        cpp_lines.append("")
        cpp_lines.append('    cout << "  attributes:" << endl;')
        for attr in ALL_ATTRS:
            cpp_lines.append(f'    cout << "    {attr}: " << entity.get_{attr}() << endl;')
        cpp_lines.append("")
        cpp_lines.append('    cout << "  sprites:" << endl;')
        cpp_lines.append('    vector<pair<string, string>> sprites = entity.get_all_sprites();')
        cpp_lines.append('    for (const auto &spr : sprites) {')
        cpp_lines.append('        cout << "    " << spr.first << ": \\"" << spr.second << "\\"" << endl;')
        cpp_lines.append('    }')
        cpp_lines.append("")
        cpp_lines.append('    cout << "  behavior:" << endl;')
        cpp_lines.append('    cout << "    ai_script: \\"" << entity.get_ai_script() << "\\"" << endl;')
        cpp_lines.append("")
        cpp_lines.append('    cout << "    attacks:" << endl;')
        cpp_lines.append('    vector<string> attack_names = entity.get_all_attack_names();')
        cpp_lines.append('    for (const auto &aname : attack_names) {')
        cpp_lines.append('        AttackInfo info = entity.get_attack_info(aname);')
        cpp_lines.append('        cout << "      " << aname << ":" << endl;')
        cpp_lines.append('        cout << "        target: \\"" << info.target_type << "\\"" << endl;')
        cpp_lines.append('        cout << "        damage_type: \\"" << info.damage_type << "\\"" << endl;')
        cpp_lines.append('        cout << "        modifier: " << info.damage_mod << endl;')
        cpp_lines.append('        cout << "        mod_type: \\"" << info.mod_type << "\\"" << endl;')
        cpp_lines.append('        if (!info.effect.empty()) {')
        cpp_lines.append('            cout << "        effect: \\"" << info.effect << "\\"" << endl;')
        cpp_lines.append('            cout << "        effect_chance: " << info.effect_chance << endl;')
        cpp_lines.append('        }')
        cpp_lines.append('    }')
        cpp_lines.append("")
        cpp_lines.append("    return 0;")
        cpp_lines.append("}")

        with open(output_file, "w") as f:
            for line in cpp_lines:
                f.write(line + "\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python generator.py <input_ast_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file, 'r') as file:
        ast_data = json.load(file)

    input_base = os.path.splitext(os.path.basename(input_file))[0]
    if input_base.endswith("_ast"):
        output_base = input_base[:-4]
    else:
        output_base = input_base
    output_file = f"{output_base}.cpp"

    generator = Generator(ast_data)
    try:
        generator.process_ast()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    generator.generate_cpp(output_file)

if __name__ == "__main__":
    main()    # Remove any trailing '_ast' if present
