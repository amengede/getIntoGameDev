use glfw::{Action, ClientApiHint, Key, PWindow, WindowHint, fail_on_errors};
mod renderer;
use renderer::renderer::State;
mod model;
use model::{world::World, game_objects::Object};
mod utility;

async fn setup_renderer(window: &mut PWindow) -> State<'_> {
    State::new(window).await
}

fn main() {
    let mut glfw = glfw::init(fail_on_errors!())
        .unwrap();
    glfw.window_hint(WindowHint::ClientApi(ClientApiHint::NoApi));
    glfw.window_hint(WindowHint::FocusOnShow(true));
    let (mut window, events) = 
        glfw.create_window(
            800, 600, "It's WGPU time.", 
            glfw::WindowMode::Windowed).unwrap();
    
    let mut state = pollster::block_on(setup_renderer(&mut window));

    state.configure_window();

    state.load_assets();

    // Build world
    let mut world = World::new();
    world.tris.push(Object {
        position: glm::Vec3::new(0.0, 0.0, -1.0),
        angle: 0.0,
        attachment: None
    });
    world.quads.push(Object {
        position: glm::Vec3::new(0.5, 0.0, -1.5),
        angle: 0.0,
        attachment: None
    });
    world.guns.push(Object {
        position: glm::Vec3::new(0.0, 0.0, 0.0),
        angle: 0.0,
        attachment: Some(String::from("mixamorig:RightHand"))
    });
    state.build_ubos_for_objects(4);
    let mut frametime: f32 = 0.0;

    while !state.window.should_close() {
        glfw.poll_events();
        
        let frame_start = glfw.get_time();

        world.update(frametime, state.window);

        for (_, event) in glfw::flush_messages(&events) {
            match event {

                //Hit escape
                glfw::WindowEvent::Key(Key::Escape, _, Action::Press, _) => {
                    state.window.set_should_close(true)
                }

                //Press or release any key
                glfw::WindowEvent::Key(key, _, Action::Press, _) => {
                    world.set_key(key, true);
                }
                glfw::WindowEvent::Key(key, _, Action::Release, _) => {
                    world.keys.insert(key, false);
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

        match state.render(&world.quads, &world.tris, &world.guns, &world.characters, &world.camera) {
            Ok(_) => {},
            Err(wgpu::SurfaceError::Lost | wgpu::SurfaceError::Outdated) => {
                state.update_surface();
                state.resize(state.size);
            },
            Err(e) => eprintln!("{:?}", e),
        }
        frametime = 1000.0 * (glfw.get_time() - frame_start) as f32;
    }
}
