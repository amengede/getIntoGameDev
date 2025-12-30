use sdl2::event::Event;
use sdl2::rect::Rect;
use sdl2::pixels::Color;

mod view;
use view::board_view;

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

    let board_view: board_view::Renderer = board_view::Renderer{
        screen_area: Rect::new(0, 0, screen_width, screen_height),
        clear_color: Color::RGB(64, 192, 255),
    };

    let mut running = true;
    let mut event_queue = sdl_context.event_pump().unwrap();

    while running {

        for event in event_queue.poll_iter() {

            match event {
                Event::Quit {..} => {
                    running = false;
                },

                Event::MouseMotion { 
                    x, y, xrel, yrel, .. } => {

                        println!("Mouse x: {}, y: {}", x, y);
                        println!("Relative x: {}, y: {}", xrel, yrel);
                    },

                _ => {}
            }
        }

        board_view.render(&mut canvas);
        canvas.present();
    }

    Ok(())
}
