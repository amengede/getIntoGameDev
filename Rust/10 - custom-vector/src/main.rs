use std::fmt::Debug;

struct Vector<T: Debug> {
    data: *mut T,
    pub size: usize,
    capacity: usize,
}

impl<T: Debug> Vector<T> {

    pub fn new() -> Self {
        let size = 0;
        let capacity = 1;
        let byte_size = capacity * std::mem::size_of::<T>();
        let alignment = std::mem::align_of::<T>();
        let layout = std::alloc::Layout::from_size_align(byte_size, alignment).unwrap();
        let data: *mut T;
        unsafe {
            data = std::alloc::alloc(layout) as *mut T;
        }

        Self {
            data,
            size,
            capacity
        }
    }

    pub fn destroy(&mut self) {
        let byte_size = self.capacity * std::mem::size_of::<T>();
        let alignment = std::mem::align_of::<T>();
        let layout = std::alloc::Layout::from_size_align(byte_size, alignment).unwrap();
        
        unsafe {
            std::alloc::dealloc(self.data as *mut u8, layout);
        }
    }

    fn resize(&mut self) {

        let byte_size = self.capacity * std::mem::size_of::<T>();
        let alignment = std::mem::align_of::<T>();
        let layout = std::alloc::Layout::from_size_align(byte_size, alignment).unwrap();
        unsafe {
            self.data = std::alloc::realloc(self.data as *mut u8, layout, 2 * byte_size) as *mut T;
        }

        self.capacity = 2 * self.capacity;
    }

    fn print(&self) {
        
        println!("---- Vector ----");
        println!("Size: {}, Capacity: {}", self.size, self.capacity);

        print!("<");
        for i in 0..self.capacity {
            unsafe {
                print!("{:?}, ", *self.data.add(i));
            }
        }
        println!(">");
    }

    fn push(&mut self, value: T) {

        while self.size >= self.capacity {
            self.resize();
        }

        unsafe {
            *self.data.add(self.size) = value;
        }

        self.size += 1;
    }

}

fn main() {
    
    let mut my_vec: Vector<i32> = Vector::new();
    my_vec.print();

    for i in 0..10 {
        my_vec.push(i);
        my_vec.print();
    }

    my_vec.destroy();
}
