#[derive(Copy, Clone, PartialEq, Eq, Hash)]
pub enum Message {
    DropPiece(usize, usize),
    DoMove,
    UndoMove,
}

pub struct System {
    pub message_queue: Vec<Message>,
    observers: Vec<*mut Vec<Message>>,
}

impl System {
    pub fn new() -> Self {
        System { message_queue: Vec::new(), observers: Vec::new() }
    }

    pub fn add_observer(&mut self, observer: *mut Vec<Message>) {
        self.observers.push(observer);
    } 

    pub fn publish(&mut self, message: Message) {

        for i in 0..self.observers.len() {
            unsafe {
                (*self.observers[i]).push(message);
            }
        }
    }
}