rss_crawler.py
- Baixa as postagens via feed xml do blog
- http://cinebancarios.blogspot.com/feeds/posts/default?alt=rss
- GET &start-index=1, GET &start-index=2, ..., GET &start-index=55
- recebe os arquivos .xml e converte para .json estruturado

json_sorter.py
- faz uma deduplicação dos arquivos .json raspados anteriormente

json_to_sqlite.py
- importa os arquivos .json para a base de dados sqlite (tabela posts)

strip_to_markdown.py
- transforma o html salvo no banco em markdown (coluna `description` => `markdown_description`)

llm_outputs.py
- consome os dados da coluna `markdown_description` e popula a tabela `llm_outputs`
- chamar com o nome da llm desejada `python3 llm_outputs gemini-2.0-flash|deepseek-chat`

## sobre a opção dos modelos utilizados

realmente não sei ='|

https://artificialanalysis.ai/models/comparisons/deepseek-v3-1-vs-gemini-2-0-flash


## database

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    link TEXT, pubDate DATETIME,
    description TEXT,
    author TEXT,
    scraped_at DATETIME,
    markdown_description TEXT
);
CREATE TABLE sqlite_sequence(name,seq);

CREATE TABLE llm_outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    llm TEXT,
    system_prompt TEXT,
    output TEXT,
    error TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    llm_output_id INTEGER,
    title TEXT,
    image_url TEXT,
    general_info TEXT,
    director TEXT,
    classification TEXT,
    excerpt TEXT,
    FOREIGN KEY (llm_output_id) REFERENCES llm_outputs(id)
);

CREATE TABLE movie_screenings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_id INTEGER,
    date DATETIME,
    FOREIGN KEY (movie_id) REFERENCES movies(id)
);
