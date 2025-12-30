mod renderer;
use renderer::renderer::State;

use glfw::{fail_on_errors, Action, Key, WindowHint, ClientApiHint};
mod model;
use model::{game_objects::Object, world::World};

async fn run() {

    let mut glfw = glfw::init(fail_on_errors!())
        .unwrap();
    glfw.window_hint(WindowHint::ClientApi(ClientApiHint::NoApi));
    let (mut window, events) = 
        glfw.create_window(
            800, 600, "It's WGPU time.", 
            glfw::WindowMode::Windowed).unwrap();
    
    let mut state = State::new(&mut window).await;

    state.window.set_framebuffer_size_polling(true);
    state.window.set_key_polling(true);
    state.window.set_mouse_button_polling(true);
    state.window.set_pos_polling(true);

    // Build world
    let mut world = World::new();
    world.tris.push(Object {
        position: glm::Vec3::new(0.0, 0.0, -1.0),
        angle: 0.0
    });
    world.quads.push(Object {
        position: glm::Vec3::new(0.5, 0.0, -2.0),
        angle: 0.0
    });
    state.build_ubos_for_objects(2);

    while !state.window.should_close() {
        glfw.poll_events();

        world.update(16.67);

        for (_, event) in glfw::flush_messages(&events) {
            match event {

                //Hit escape
                glfw::WindowEvent::Key(Key::Escape, _, Action::Press, _) => {
                    state.window.set_should_close(true)
                }

                //Window was moved
                glfw::WindowEvent::Pos(..) => {
                    state.update_surface();
                    state.resize(state.size);
                }

                //Window was resized
                glfw::WindowEvent::FramebufferSize(width, height) => {
                    state.update_surface();
                    state.resize((width, height));
                }
                _ => {}
            }
        }

        match state.render(&world.quads, &world.tris) {
            Ok(_) => {},
            Err(wgpu::SurfaceError::Lost | wgpu::SurfaceError::Outdated) => {
                state.update_surface();
                state.resize(state.size);
            },
            Err(e) => eprintln!("{:?}", e),
        }
    }
}

fn main() {
    pollster::block_on(run());
}
