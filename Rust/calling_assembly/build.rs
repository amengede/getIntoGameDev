fn main() {
    println!("cargo:rerun-if-changed=NULL");
    cc::Build::new().file("src/asm_stuff.s").compile("my_asm_library");
}