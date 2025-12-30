use std::collections::HashMap;
use crate::model::common::ObjectType;

pub const ANIMATION_TYPE_DEFAULT: u8 = 0;
pub const ANIMATION_TYPE_WALK: u8 = 1;
pub const ANIMATION_TYPE_WALK_2: u8 = 2;

pub fn get_animation_lookup() -> HashMap<ObjectType, HashMap<String, u8>> {

    let mut animation_lookup: HashMap<ObjectType, HashMap<String, u8>> = HashMap::new();
    
    let codes: HashMap<String, u8> =
        HashMap::from([
            (String::from("T_Pose"), ANIMATION_TYPE_DEFAULT),
            (String::from("Walk"), ANIMATION_TYPE_WALK),
            (String::from("WALK_2"), ANIMATION_TYPE_WALK_2)]);
    animation_lookup.insert(ObjectType::Girl, codes);
    
    animation_lookup
}