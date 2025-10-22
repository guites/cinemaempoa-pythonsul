# Extração de filmes do site CineBancários

Este projeto tem como objetivo principal automatizar a extração dos filmes anúnciados via postagem no blog <https://cinebancarios.blogspot.com/>.

O CineBancários é um cinema de rua de Porto Alegre que existe desde 2008. Ele exibe filmes nacionais e estrangeiros de terça a domingo com preços acessíveis para a população.

O [cinemaempoa](https://cinemaempoa.com.br/about) é um site que agrega os filmes em exibição nos cinemas alternativos de Porto Alegre. 

Este projeto surgiu da necessidade de melhorar o processo de coleta de dados, explorando **o uso de modelos de linguagem via APIs** para redução dos erros de extração e **proposta de um sistema de alertas** para checagem humana dos dados importados.

Abaixo, um diagrama em alto nível da estratégia utilizada.

[![](https://mermaid.ink/img/pako:eNpFkEtuwjAQhq9izZogyAuSRSVIom7orqsmXYzwJESN7ch2Ci3iMFUXPQgXq0OBevHrn8c3M_IRtooTpOB5XiVtaztiFRQHq_H8c_5WjCvD6rYTZJxlprXEslbSGuX2_KVbZSqo5AWuO7Xf7lBb9pxXkrm3KnO1l51Czjga1itjsSFpXv_K6_JZozS10uK6jAQTqN-4o649WVnI91axHjUyN2OzebrheZkpMeb_D9Vkhs6is9eeonykewMx7EhbvBVXzPMe1qNko-SjFDCBRrccUqsHmoAgd9wYwnGEKrA7ElRB6iynGt268QNODutRviglbqRWQ7ODtMbOuGjoOVrKW2w0intWk-SkMzVIC6kfBfPLFEiPcHBxuJzG_mIWJUkQR34QhhP4gHQ-D6d-tAiD-SyY-QuXPk3g87J4No2TKAn9ZZDEDlr64ekXWq2dCw?type=png)](https://mermaid.live/edit#pako:eNpFkEtuwjAQhq9izZogyAuSRSVIom7orqsmXYzwJESN7ch2Ci3iMFUXPQgXq0OBevHrn8c3M_IRtooTpOB5XiVtaztiFRQHq_H8c_5WjCvD6rYTZJxlprXEslbSGuX2_KVbZSqo5AWuO7Xf7lBb9pxXkrm3KnO1l51Czjga1itjsSFpXv_K6_JZozS10uK6jAQTqN-4o649WVnI91axHjUyN2OzebrheZkpMeb_D9Vkhs6is9eeonykewMx7EhbvBVXzPMe1qNko-SjFDCBRrccUqsHmoAgd9wYwnGEKrA7ElRB6iynGt268QNODutRviglbqRWQ7ODtMbOuGjoOVrKW2w0intWk-SkMzVIC6kfBfPLFEiPcHBxuJzG_mIWJUkQR34QhhP4gHQ-D6d-tAiD-SyY-QuXPk3g87J4No2TKAn9ZZDEDlr64ekXWq2dCw)

<details>
  <summary>Código do diagrama</summary>
    <pre>```
    ---
    title "Extração dos filmes do site CineBancários"
    ---
    flowchart LR
        A[Download das postagens]
        B[Transformação em markdown]
        C[Envio para as LLMs]
        D[Comparação dos resultados]
        E[Geração de alertas]
        A -->B -->C -->D -->E
    ```</pre>

</details>

Cada uma das etapas foi implementada através de um script Python separado, conforme o diagrama abaixo:

[![](https://mermaid.ink/img/pako:eNqNkUtyGjEQhq_SpTVDwTzxVMpVweP4AM4qMxTVnmlAth5jSQOOgcNkm2v4YpFwIMUu2kit7v_T3609a3VHrGRRFDXKcScIGvZIr8PHb9VyhI7Atob3zsLguODv2GkLPQkNvdHP5HTDGnVSr4TetRs0Dr5XjQK_vtbG2mVrcCfILCCKbg9PyN8Q0CO0dbgmZYGg1WpLxhH0aBCerVYHmNdhXzq9tK-CO1p8IucQjT3mEcX2GnOAu3qOqtXBchdc_lNEt1DV1vk2Ak-ieen0Tv3NV_AlIOFwcaFh46QAkjCWneee6wLnvhZCLvXg-sGdX7g_E54G2-KVpXPBZ96eXK-4kBTa3mjz8ctwfVUY6kht_ej9fGXv_HAkXKDy8K1-IMkVX_y34qGuiHpL9LJgI7Y2vGOlMwONmCQjMYRsH2gNcxuS1LDSHzta4SBc-N2jl_Wofmgtz0qjh_WGlSsU1kdD36GjiuPaoLzcGlIdmTs9KMfKOJ9mJwor9-zNx7NknMfFJE3zoiiSNB2xn6ycJtk4zoo0mU6SSRyujyP2fnp3Ms5vspvU6-J8ls2KfHb8Ay6A5LE?type=png)](https://mermaid.live/edit#pako:eNqNkUtyGjEQhq_SpTVDwTzxVMpVweP4AM4qMxTVnmlAth5jSQOOgcNkm2v4YpFwIMUu2kit7v_T3609a3VHrGRRFDXKcScIGvZIr8PHb9VyhI7Atob3zsLguODv2GkLPQkNvdHP5HTDGnVSr4TetRs0Dr5XjQK_vtbG2mVrcCfILCCKbg9PyN8Q0CO0dbgmZYGg1WpLxhH0aBCerVYHmNdhXzq9tK-CO1p8IucQjT3mEcX2GnOAu3qOqtXBchdc_lNEt1DV1vk2Ak-ieen0Tv3NV_AlIOFwcaFh46QAkjCWneee6wLnvhZCLvXg-sGdX7g_E54G2-KVpXPBZ96eXK-4kBTa3mjz8ctwfVUY6kht_ej9fGXv_HAkXKDy8K1-IMkVX_y34qGuiHpL9LJgI7Y2vGOlMwONmCQjMYRsH2gNcxuS1LDSHzta4SBc-N2jl_Wofmgtz0qjh_WGlSsU1kdD36GjiuPaoLzcGlIdmTs9KMfKOJ9mJwor9-zNx7NknMfFJE3zoiiSNB2xn6ycJtk4zoo0mU6SSRyujyP2fnp3Ms5vspvU6-J8ls2KfHb8Ay6A5LE)

<details>
  <summary>Código do diagrama</summary>
    <pre>```
    ---
    title "Sequência de scripts utilizados pelo projeto"
    ---
    flowchart TD
        A[rss_crawler] -->|baixa as postagens e converte para json| B[json_to_sqlite]
        B -.->|Salva as postagens| C[Banco de dados]
        B --> D[strip_to_markdown]
        D <-.-> |converte o html em .md| C
        D --> E[llm_outputs]
        E <-.-> |busca postagens| C
        E -.-> |salva filmes e horários| C
        E --> |envia prompt com a postagem|F[Gemini]
        E --> |envia prompt com a postagem|G[Deepseek]

    ```</pre>

</details>

