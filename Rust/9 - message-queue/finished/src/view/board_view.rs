use sdl2::image::LoadTexture;
use sdl2::rect::Rect;
use sdl2::rect::Point;
use sdl2::pixels::Color;
use sdl2::render::Canvas;
use sdl2::render::TextureCreator;
use sdl2::video::Window;
use sdl2::render::Texture;
use sdl2::video::WindowContext;

use crate::model::game::BoardPiece;

pub struct Renderer<'a> {
    pub screen_area: Rect,
    pub clear_color: Color,
    pieces: Texture<'a>,
}

impl<'a> Renderer<'a> {

    pub fn new(
        width: u32, height: u32, 
        texture_creator: &'a TextureCreator<WindowContext>) -> Self {

        let _pieces = texture_creator.load_texture("img/pieces.jpg");

        Self {
            screen_area: Rect::new(0, 0, width, height),
            clear_color: Color::RGB(64, 192, 255),
            pieces: _pieces.ok().unwrap(),
        }
    }

    pub fn render(
        &self, 
        canvas: &mut Canvas<Window>,
        board: &[[BoardPiece; 5]; 5]) {

        //background
        canvas.set_draw_color(self.clear_color);
        canvas.fill_rect(self.screen_area).ok().unwrap_or_default();

        //lines
        self.draw_lines(canvas);

        //pieces
        self.draw_pieces(canvas, board);
    }

    fn draw_lines(&self, canvas: &mut Canvas<Window>) {

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

    fn draw_pieces(
        &self, 
        canvas: &mut Canvas<Window>, 
        board: &[[BoardPiece; 5]; 5]) {

        let width: i32 = self.screen_area.w / 5;
        let height: i32 = self.screen_area.h / 5;

        for i in 0i32..5 {
            let row: usize = i.try_into().unwrap();
            for j in 0i32..5 {
                let col: usize = j.try_into().unwrap();
                if board[row][col] == BoardPiece::None {
                    continue;
                }

                let image: &Texture<'a> = &self.pieces;
                let image_attributes = image.query();
                let mut src_rect:Rect = Rect::new(
                    0, 
                    (image_attributes.height / 2).try_into().unwrap(), 
                    image_attributes.width / 2, 
                    image_attributes.height / 2);
                if board[row][col] == BoardPiece::Red {
                    src_rect.set_x((image_attributes.width / 2).try_into().unwrap());
                    src_rect.set_y(0);
                }

                let dst_rect: Rect = Rect::new(
                    width / 4 + width * j, height / 4 + height * i,
                    (width / 2).try_into().unwrap(), 
                    (height/ 2).try_into().unwrap()
                );
                canvas.copy(image, src_rect, dst_rect).ok().unwrap();
            }
        }
    }

}