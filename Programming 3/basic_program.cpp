#include <iostream>
#include <vector>
#include <string>
#include <utility>

using namespace std;

struct AttackInfo {
    string damage_type;
    string target_type;
    float damage_mod;
    string mod_type;
    string effect;
    float effect_chance;
};

class Cait {
public:
    int hp = 500;
    int p_attack = 35;
    int m_attack = 1;
    int p_defense = 50;
    int m_defense = 1;
    int speed = 1;
    int level = 1;
    int exp = 1;
    string entity_name_str = "Cait";
    string sprite_idle = "sprite_default";
    string sprite_move = "cait_mov";
    string ai_script = "behavior_default";

private:
    vector<pair<string,string>> sprites_data;
    vector<pair<string, AttackInfo>> attacks_data;

public:
    Cait() {
        // Initialize sprites
        sprites_data.emplace_back("idle", sprite_idle);
        sprites_data.emplace_back("move", sprite_move);

        // Initialize attacks
        {
            AttackInfo info;
            info.damage_type = "physical";
            info.target_type = "multi";
            info.damage_mod = 1.0f;
            info.mod_type = "additive";
            info.effect = "poison";
            info.effect_chance = 0.0f;
            attacks_data.emplace_back("poison", info);
        }
        {
            AttackInfo info;
            info.damage_type = "physical";
            info.target_type = "single";
            info.damage_mod = 1.0f;
            info.mod_type = "additive";
            info.effect = "";
            info.effect_chance = 0.0f;
            attacks_data.emplace_back("basic", info);
        }
    }
    int get_hp() const { return hp; }
    int get_p_attack() const { return p_attack; }
    int get_m_attack() const { return m_attack; }
    int get_p_defense() const { return p_defense; }
    int get_m_defense() const { return m_defense; }
    int get_speed() const { return speed; }
    int get_level() const { return level; }
    int get_exp() const { return exp; }
    string get_entity_name() const { return entity_name_str; }
    string get_ai_script() const { return ai_script; }

    int deal_damage(string damage_type, string target_type, int damage, float damage_mod, string mod_type, string effect, float effect_chance) {
        // Placeholder implementation.
        return 0;
    }

    vector<pair<string,string>> get_all_sprites() const {
        return sprites_data;
    }

    vector<string> get_all_attack_names() const {
        vector<string> names;
        for (const auto &p : attacks_data) {
            names.push_back(p.first);
        }
        return names;
    }

    AttackInfo get_attack_info(const string &attack_name) const {
        for (const auto &p : attacks_data) {
            if (p.first == attack_name) return p.second;
        }
        // Return default AttackInfo if not found
        AttackInfo empty_info;
        empty_info.damage_type = "physical";
        empty_info.target_type = "single";
        empty_info.damage_mod = 1.0f;
        empty_info.mod_type = "additive";
        empty_info.effect = "";
        empty_info.effect_chance = 0.0f;
        return empty_info;
    }

    int basic_attack() {
        AttackInfo info = get_attack_info("basic");
        int damage = (info.damage_type == "physical") ? p_attack : m_attack;
        return deal_damage(info.damage_type, info.target_type, damage, info.damage_mod, info.mod_type, info.effect, info.effect_chance);
    }

    int poison_attack() {
        AttackInfo info = get_attack_info("poison");
        int damage = (info.damage_type == "physical") ? p_attack : m_attack;
        return deal_damage(info.damage_type, info.target_type, damage, info.damage_mod, info.mod_type, info.effect, info.effect_chance);
    }
};

int main() {
    Cait entity;

    cout << "Cait:" << endl;
    cout << "  name: \"" << entity.get_entity_name() << "\"" << endl;

    cout << "  attributes:" << endl;
    cout << "    hp: " << entity.get_hp() << endl;
    cout << "    p_attack: " << entity.get_p_attack() << endl;
    cout << "    m_attack: " << entity.get_m_attack() << endl;
    cout << "    p_defense: " << entity.get_p_defense() << endl;
    cout << "    m_defense: " << entity.get_m_defense() << endl;
    cout << "    speed: " << entity.get_speed() << endl;
    cout << "    level: " << entity.get_level() << endl;
    cout << "    exp: " << entity.get_exp() << endl;

    cout << "  sprites:" << endl;
    vector<pair<string, string>> sprites = entity.get_all_sprites();
    for (const auto &spr : sprites) {
        cout << "    " << spr.first << ": \"" << spr.second << "\"" << endl;
    }

    cout << "  behavior:" << endl;
    cout << "    ai_script: \"" << entity.get_ai_script() << "\"" << endl;

    cout << "    attacks:" << endl;
    vector<string> attack_names = entity.get_all_attack_names();
    for (const auto &aname : attack_names) {
        AttackInfo info = entity.get_attack_info(aname);
        cout << "      " << aname << ":" << endl;
        cout << "        target: \"" << info.target_type << "\"" << endl;
        cout << "        damage_type: \"" << info.damage_type << "\"" << endl;
        cout << "        modifier: " << info.damage_mod << endl;
        cout << "        mod_type: \"" << info.mod_type << "\"" << endl;
        if (!info.effect.empty()) {
            cout << "        effect: \"" << info.effect << "\"" << endl;
            cout << "        effect_chance: " << info.effect_chance << endl;
        }
    }

    return 0;
}
