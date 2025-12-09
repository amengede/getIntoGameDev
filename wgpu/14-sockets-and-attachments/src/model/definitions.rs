use std::collections::HashMap;

pub const ANIMATION_TYPE_DEFAULT: u8 = 0;
pub const ANIMATION_TYPE_WALK: u8 = 1;
pub const ANIMATION_TYPE_WALK_2: u8 = 2;

pub const OBJECT_TYPE_GIRL: u8 = 0;

pub fn get_animation_lookup() -> HashMap<u8, HashMap<String, u8>> {

    let mut animation_lookup: HashMap<u8, HashMap<String, u8>> = HashMap::new();
    
    let codes: HashMap<String, u8> =
        HashMap::from([
            (String::from("T_Pose"), ANIMATION_TYPE_DEFAULT),
            (String::from("Walk"), ANIMATION_TYPE_WALK),
            (String::from("WALK_2"), ANIMATION_TYPE_WALK_2)]);
    animation_lookup.insert(OBJECT_TYPE_GIRL, codes);
    
    animation_lookup
}