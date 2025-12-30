use sdl2::rect::Rect;
use sdl2::rect::Point;
use sdl2::pixels::Color;
use sdl2::render::Canvas;
use sdl2::video::Window;

pub struct Renderer {
    pub screen_area: Rect,
    pub clear_color: Color,
}

impl Renderer {

    pub fn render(&self, canvas: &mut Canvas<Window>) {

        //background
        canvas.set_draw_color(self.clear_color);
        canvas.fill_rect(self.screen_area).ok().unwrap_or_default();

        //lines
        canvas.set_draw_color(Color::RGB(0, 0, 0));
        let cell_width: i32 = self.screen_area.w / 5;
        let cell_height: i32 = self.screen_area.h / 5;
        for i in 0..5 {

            //horizontal
            canvas.draw_line(
                Point::new(cell_width / 2, cell_height / 2 + i * cell_height), 
                Point::new(self.screen_area.w - cell_width / 2, cell_height / 2 + i * cell_height)
            ).ok().unwrap_or_default();

            //vertical
            canvas.draw_line(
                Point::new(cell_width / 2 + i * cell_width, cell_height / 2), 
                Point::new(cell_width / 2 + i * cell_width, self.screen_area.h - cell_height / 2)
            ).ok().unwrap_or_default();

            //diagonal up-right a
            canvas.draw_line(
                Point::new(cell_width / 2, cell_height / 2 + i * cell_height), 
                Point::new(cell_width / 2 + i * cell_width, cell_height / 2)
            ).ok().unwrap_or_default();

            //diagonal up-right b
            canvas.draw_line(
                Point::new(cell_width / 2 + i * cell_width, self.screen_area.h - cell_height / 2), 
                Point::new(self.screen_area.w - cell_width / 2, cell_height / 2 + i * cell_height)
            ).ok().unwrap_or_default();

            //diagonal up-down a
            canvas.draw_line(
                Point::new(cell_width / 2, cell_height / 2 + i * cell_height), 
                Point::new(self.screen_area.w - (cell_width / 2 + i * cell_width), self.screen_area.h - cell_height / 2)
            ).ok().unwrap_or_default();

            //diagonal up-down b
            canvas.draw_line(
                Point::new(cell_width / 2 + i * cell_width, cell_height / 2), 
                Point::new(self.screen_area.w - cell_width / 2, self.screen_area.h - (cell_height / 2 + i * cell_height))
            ).ok().unwrap_or_default();
        }
    }
}