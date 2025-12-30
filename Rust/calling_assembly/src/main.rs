extern "C" {
    fn sign_asm(x: i64)->i64;
}

fn main() {
    unsafe {
        println!("sign(-3) = {}", sign_asm(-3));
        println!("sign(0) = {}", sign_asm(0));
        println!("sign(7) = {}", sign_asm(7));
    }
}
