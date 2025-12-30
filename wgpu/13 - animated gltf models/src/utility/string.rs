pub fn split(line: &str, token: &str) -> Vec<String> {
    let mut words: Vec<String> = Vec::new();
    let iterator = line.split(token);

    for word in iterator {
        words.push(word.to_string());
    }

    words
}