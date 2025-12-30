// rustup upgrade -- nightly
// rustup default nightly

#![feature(portable_simd, vec_into_raw_parts)]
use std::simd::f32x8;

fn main() {

    let mut x: Vec<f32> = Vec::new();
    let mut y: Vec<f32> = Vec::new();

    // Set
    for i in 1..8_000_000 {
        x.push(i as f32);
        y.push(i as f32);
    }

    // Verify
    print!("Initial Layout: ");
    for i in 0..16 {
        print!("<{}, {}> ", x[i], y[i]);
    }
    println!();

    // Modify
    let mut start = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap();
    for i in 0..x.len() {
        x[i] = x[i] + y[i];
    }
    let mut end = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap();
    println!("naive: {:?}", end - start);

    // Verify
    print!("After Naive: ");
    for i in 0..16 {
        print!("<{}, {}> ", x[i], y[i]);
    }
    println!();

    // Reset
    x.clear();
    y.clear();
    for i in 1..8_000_000 {
        x.push(i as f32);
        y.push(i as f32);
    }

    // Verify
    print!("Reset Layout: ");
    for i in 0..16 {
        print!("<{}, {}> ", x[i], y[i]);
    }
    println!();

    // Get SIMD view of data
    let x_chunks: *mut f32x8;
    {
        let (ptr, length, capacity) = x.into_raw_parts();
        x_chunks = ptr as *mut f32x8;
        unsafe {
            x = Vec::from_raw_parts(ptr, length, capacity);
        }
    }

    let y_chunks: *mut f32x8;
    {
        let (ptr, length, capacity) = y.into_raw_parts();
        y_chunks = ptr as *mut f32x8;
        unsafe {
            y = Vec::from_raw_parts(ptr, length, capacity);
        }
    }
    let chunk_count = x.len() / 8;

    // Modify
    start = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap();
    unsafe {
        for i in 0..chunk_count {
            *x_chunks.add(i) = *x_chunks.add(i) + *y_chunks.add(i);
        }
    }
    end = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap();
    println!("simd: {:?}", end - start);

    // Verify
    print!("After SIMD: ");
    for i in 0..16 {
        print!("<{}, {}> ", x[i], y[i]);
    }
    println!();
}