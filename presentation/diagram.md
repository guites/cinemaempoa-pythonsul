---
title "Sequência de scripts utilizados pelo projeto"
---
flowchart TD
    A[crawler] -->|baixa postagem| B[strip_to_text]
    B -.-> |converte o html<br> em texto| C[llm_outputs]
    C --> |envia prompt| D[Gemini/Deepseek]
    D --> |Extrai filmes e horários em formato json| H[Salva arquivos em disco]
    H --> A
