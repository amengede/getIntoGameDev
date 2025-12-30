use sdl2::mixer;

use crate::common::common::{Message, System};

use std::collections::HashMap;

pub struct AudioSystem {
    pub system: System,
    channel: mixer::Channel,
    chunks: HashMap<Message, mixer::Chunk>,
}

impl AudioSystem {

    pub fn new() -> Self {
        
        let system = System::new();

        mixer::open_audio(44100, mixer::DEFAULT_FORMAT, 2, 4096).unwrap();

        let channel = mixer::Channel(0);

        let mut chunks: HashMap<Message, mixer::Chunk> = HashMap::new();
        chunks.insert(Message::DoMove, mixer::Chunk::from_file("sfx/click_on.wav").unwrap());
        chunks.insert(Message::UndoMove, mixer::Chunk::from_file("sfx/click_off.wav").unwrap());

        Self {
            system,
            channel,
            chunks
        }
    }

    pub fn update(&mut self) {

        for i in 0..self.system.message_queue.len() {

            let message = self.system.message_queue[i];

            if !self.chunks.contains_key(&message) {
                continue;
            }
            
            mixer::Channel::play(self.channel, &self.chunks[&message], 1).unwrap();
        }

        self.system.message_queue.clear();
    }
}