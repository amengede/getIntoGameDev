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
    history: Vec<PieceDropCommand>,
    history_pos: usize,
}

impl GameState {

    pub fn new() -> Self {
        
        Self{
            board: make_blank_board(),
            current_player: BoardPiece::Red,
            pieces_dropped: [0,0],
            history: Vec::new(),
            history_pos: 0
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
        
        let command = PieceDropCommand{
            row: row,
            col: col,
            player: self.current_player
        };

        if !command.is_valid(self) {
            return;
        }
        
        if self.history.len() > 0 {
            let elements_to_clear = self.history.len() - (self.history_pos+1);
            for _ in 0..elements_to_clear {
                self.history.pop();
            }
        }

        command.perform(self);
        self.history.push(command);
        self.history_pos = self.history.len() - 1;
    }

    pub fn redo_action(&mut self) {

        if (self.history_pos + 1) >= self.history.len() {
            return;
        }

        self.history_pos += 1;

        let command: PieceDropCommand = self.history[self.history_pos].copy();
        command.perform(self);
    }

    pub fn undo_action(&mut self) {

        if self.history.len() == 0 {
            return;
        }

        let command: PieceDropCommand = self.history[self.history_pos].copy();
        command.undo(self);
        
        if self.history_pos == 0 {
            return;
        }

        self.history_pos -= 1;
    }

    fn index_of_piece(&self, piece: BoardPiece) -> usize {
        
        if piece == BoardPiece::Red {
            return 0;
        }
        return 1;
    }

}

/*Task B: make a command object, which can be done and undone */
pub struct PieceDropCommand {
    pub row: usize,
    pub col: usize,
    pub player: BoardPiece,
}

impl PieceDropCommand {

    pub fn perform(&self, game: &mut GameState) {

        game.pieces_dropped[game.index_of_piece(self.player)] += 1;
        game.board[self.row][self.col] = self.player;

        if self.player == BoardPiece::Red {
            game.current_player = BoardPiece::Black;
        }
        else {
            game.current_player = BoardPiece::Red;
        }
    }

    pub fn undo(&self, game: &mut GameState) {

        game.pieces_dropped[game.index_of_piece(self.player)] -= 1;
        game.board[self.row][self.col] = BoardPiece::None;

        game.current_player = self.player;
    }

    pub fn is_valid(&self, game: & GameState) -> bool {

        if self.row > 4 || self.col > 4 {
            return false;
        }

        if game.pieces_dropped[game.index_of_piece(self.player)] >= 4 {
            return false;
        }

        if game.board[self.row][self.col] != BoardPiece::None {
            return false;
        }

        return true;
    }

    pub fn copy(&self) -> Self{
        Self{
            row: self.row,
            col: self.col,
            player: self.player
        }
    }
}