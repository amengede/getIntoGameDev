use std::collections::HashMap;

fn say_hello() {
    println!("Hello, world!");
}

fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn mul(a: i32, b: i32) -> i32 {
    a * b
}

fn report(something: &str) {
    println!("{}", something);
}

fn report_result(result: i32) {
    println!("Result is {}", result);
}

#[derive(Eq, Hash, PartialEq)]
enum StateType {
    Add,
    Multiply,
    NoChange
}

fn start_adding() {
    println!("Hello, I am adding now!");
}

fn act_add(a: i32, b: i32) -> (i32, StateType) {
    let result = a + b;
    println!("{} + {} = {}", a, b, result);
    (result, StateType::Multiply)
}

fn stop_adding() {
    println!("Ok, I'll stop adding now.");
}

fn start_multiplying() {
    println!("Hello, I am multiplying now!");
}

fn act_multiply(a: i32, b: i32) -> (i32, StateType) {
    let result = a * b;
    println!("{} * {} = {}", a, b, result);
    (a * b, StateType::Add)
}

fn stop_multiplying() {
    println!("Ok, I'll stop multiplying now.");
}

struct State {
    enter: fn(),
    update: fn(i32, i32) -> (i32, StateType),
    exit: fn(),
}

fn main() {
    let just_do_it: fn() = say_hello;
    just_do_it();

    let just_do_it: fn(i32, i32) -> i32 = add;
    let result = just_do_it(2,4);

    let just_do_it: fn(i32) = report_result;
    just_do_it(result);

    let just_do_it: fn(&str) = report;
    just_do_it("Guess I'm multiplying now");

    let just_do_it: fn(i32, i32) -> i32 = mul;
    let result = just_do_it(2,4);

    let just_do_it: fn(i32) = report_result;
    just_do_it(result);

    let mut states: HashMap<StateType, State> = HashMap::new();
    states.insert(StateType::Add, 
        State{
            enter: start_adding, 
            update: act_add, 
            exit: stop_adding});
    
    states.insert(StateType::Multiply, 
        State{
            enter: start_multiplying, 
            update: act_multiply, 
            exit: stop_multiplying});
    
    let mut current_state: StateType = StateType::Add;
    (states[&current_state].enter)();

    for _ in 0..3 {
        let result = (states[&current_state].update)(2, 4);
        match result.1 {
            StateType::NoChange => {},
            new_state => {
                (states[&current_state].exit)();
                current_state = new_state;
                (states[&current_state].enter)();
            }
        }
    }
    (states[&current_state].exit)();
}
