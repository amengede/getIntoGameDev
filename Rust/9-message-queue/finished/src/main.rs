use sdl2::event::Event;

mod audio;
use audio::audio::AudioSystem;

mod view;
use view::board_view::Renderer;

mod model;
use model::game::GameState;

mod common;
use common::common::{System, Message};

fn main() -> Result<(), String> {

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

    let texture_creator = canvas.texture_creator();
    
    let board_view: Renderer = Renderer::new(
        screen_width, screen_height, &texture_creator
    );

    let mut game_state: GameState = GameState::new();

    let mut running = true;
    let mut event_queue = sdl_context.event_pump().unwrap();

    let mut audio_system = AudioSystem::new();

    let mut system = System::new();

    // Hook everything up
    system.add_observer(&mut game_state.system.message_queue);
    game_state.system.add_observer(&mut audio_system.system.message_queue);

    while running {

        for event in event_queue.poll_iter() {

            match event {
                Event::Quit {..} => {
                    running = false;
                },

                Event::MouseButtonDown { x , y, .. } => {
                    let row: usize = (5 * y / board_view.screen_area.h).try_into().unwrap();
                    let col: usize = (5 * x / board_view.screen_area.w).try_into().unwrap();
                    system.publish(Message::DropPiece(row, col));
                },
                Event::KeyDown { keycode, .. } => {
                    if keycode.unwrap() == sdl2::keyboard::Keycode::U {
                        system.publish(Message::UndoMove);
                    }
                    else if keycode.unwrap() == sdl2::keyboard::Keycode::R {
                        system.publish(Message::DoMove);
                    }
                }
                _ => {}
            }
        }

        game_state.update();
        audio_system.update();

        board_view.render(&mut canvas, &game_state.board);
        canvas.present();
    }

    Ok(())
}
