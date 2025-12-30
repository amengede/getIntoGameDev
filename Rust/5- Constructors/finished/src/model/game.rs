#[derive(Clone, Copy, PartialEq, Eq)]
pub enum BoardPiece {
    Red,
    Black,
    None,
}

pub fn make_blank_board() -> [[BoardPiece; 5]; 5] {
    [[BoardPiece::None; 5]; 5]
}
pub struct GameState {
    pub board: [[BoardPiece; 5]; 5],
    pub current_player: BoardPiece,
    pub pieces_dropped: [i32; 2],
}

impl GameState {

    pub fn new() -> Self {
        
        Self{
            board: make_blank_board(),
            current_player: BoardPiece::Red,
            pieces_dropped: [0,0]
        }
    }

    pub fn jumble_board(&mut self) {
        self.board[1][0] = BoardPiece::Red;
        self.board[2][0] = BoardPiece::Black;
    }

    pub fn print_board(&self) {

        let mut label: String;
        for row in 0..5 {
            for col in 0..5 {
                if self.board[row][col] == BoardPiece::None {
                    label = "-".to_string();
                }
                else if self.board[row][col] == BoardPiece::Red {
                    label = "R".to_string();
                }
                else {
                    label = "B".to_string();
                }
                print!("{}", label)
            }
            println!();
        }
        println!();
    }

    pub fn handle_click(&mut self, row: usize, col: usize) {
        //println!("Clicked at ({col}, {row})");
        if row > 4 || col > 4 {
            return;
        }
        if self.pieces_dropped[self.index_of_piece(self.current_player)] >= 4 {
            return;
        }
        if self.board[row][col] != BoardPiece::None {
            return;
        }

        self.board[row][col] = self.current_player;

        self.next_turn();
    }

    fn next_turn(&mut self) {

        self.pieces_dropped[self.index_of_piece(self.current_player)] += 1;

        if self.current_player == BoardPiece::Red {
            self.current_player = BoardPiece::Black;
        }
        else {
            self.current_player = BoardPiece::Red;
        }
    }

    fn index_of_piece(&self, piece: BoardPiece) -> usize {
        
        if piece == BoardPiece::Red {
            return 0;
        }
        return 1;
    }

}