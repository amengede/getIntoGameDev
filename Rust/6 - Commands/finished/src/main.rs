use sdl2::event::Event;

mod view;
use view::board_view::Renderer;

mod model;
use model::game::{GameState, PieceDropCommand};

fn test_task_a() {
    let mut v: Vec<u32> = Vec::new();
    v.push(10);
    v.push(28);

    let mut size: usize = v.len();
    let mut capacity: usize = v.capacity();

    println!("Our vector has {} elements", size);
    println!("Our vector has space reserved for {} elements",
                capacity);
    for i in 0..(size - 1) {
        println!("v[{}]: {}", i, v[i]);
    }

    v.pop();

    size = v.len();
    capacity = v.capacity();

    println!("Our vector has {} elements", size);
    println!("Our vector has space reserved for {} elements",
                capacity);
    for i in 1..(size - 1) {
        println!("v[{}]: {}", i, v[i]);
    }

    v.push(10);
    v.push(28);
    v.push(10);
    v.push(28);
    v.push(10);
    v.push(28);
    size = v.len();
    for _ in 1..(size - 4) {
        v.pop();
    }

    size = v.len();
    capacity = v.capacity();

    println!("Our vector has {} elements", size);
    println!("Our vector has space reserved for {} elements",
                capacity);
    for i in 0..(size - 1) {
        println!("v[{}]: {}", i, v[i]);
    }
}

fn test_task_b(mut game: &mut GameState) {
    let command1 = PieceDropCommand{row: 0, col:1, player: model::game::BoardPiece::Red};
    let command2 = PieceDropCommand{row: 0, col:1, player: model::game::BoardPiece::Black};
    command1.perform(&mut game);
    println!("Second drop valid: {}", command2.is_valid(game));
    command1.undo(&mut game);
    println!("Second drop valid: {}", command2.is_valid(game));
    command2.perform(&mut game);
}

fn main() -> Result<(), String> {

    /*Task A: make a growable and shrinkable array */
    //test_task_a();

    let screen_width = 800;
    let screen_height = 600;
    
    let sdl_context = sdl2::init()?;
    let video_subsystem = sdl_context.video()?;
    let window = video_subsystem.window("Rust!", screen_width, screen_height)
        .build()
        .unwrap();
    
    let mut canvas = window.into_canvas()
        .build()
        .unwrap();

    let board_view: Renderer = Renderer::new(
        screen_width, screen_height
    );

    let mut game_state: GameState = GameState::new();

    /*Test our new Commands! */
    //test_task_b(&mut game_state);

    let mut running = true;
    let mut event_queue = sdl_context.event_pump().unwrap();

    while running {

        for event in event_queue.poll_iter() {

            match event {
                Event::Quit {..} => {
                    running = false;
                },

                Event::MouseButtonDown { x , y, .. } => {
                    let row: usize = (5 * y / board_view.screen_area.h).try_into().unwrap();
                    let col: usize = (5 * x / board_view.screen_area.w).try_into().unwrap();
                    game_state.handle_click(row, col);
                },
                Event::KeyDown { keycode, .. } => {
                    if keycode.unwrap() == sdl2::keyboard::Keycode::U {
                        game_state.undo_action();
                    }
                    else if keycode.unwrap() == sdl2::keyboard::Keycode::R {
                        game_state.redo_action();
                    }
                }

                _ => {}
            }
        }

        board_view.render(&mut canvas, &game_state.board);
        canvas.present();
    }

    Ok(())
}
