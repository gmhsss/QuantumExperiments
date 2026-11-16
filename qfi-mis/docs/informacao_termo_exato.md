# O que é "informação"? Termo usado no projeto

Não existe uma definição única de informação aceita por todas as ciências. Cada área usa o nome para uma quantidade diferente. O termo exato do projeto é **informação funcional (Hazen et al., 2007)**, aplicada ao espaço de soluções do MIS.

## Comparação das definições

| Definição (autor) | O que mede | Fórmula ou ideia | Serve ao projeto? |
|---|---|---|---|
| Estatística / técnica (Shannon, 1948) | Incerteza removida sobre qual mensagem foi enviada; ignora o significado | H = −Σ p log2 p; surpresa: −log2 p | Parcialmente: mede concentração, não diz se foi em soluções boas |
| Algorítmica (Kolmogorov) | Tamanho do menor programa que gera o objeto | K(x) | Não |
| Parâmetros (Fisher) | Quanto os dados dizem sobre um parâmetro | I(θ) = E[(∂ log p/∂θ)^2] | Não diretamente |
| Quântica (von Neumann; Holevo) | Mistura de um estado; informação acessível | S(ρ) = −Tr(ρ log2 ρ) | Só na versão baseada em fidelidade (QFI) |
| Semântica (Floridi) | Dados bem formados, com significado e verdadeiros | Definição qualitativa | Não: não é quantitativa |
| Relacional (Bateson) | "Uma diferença que faz diferença" | Ideia qualitativa | Inspira, mas não mede |
| Física (Landauer; Wheeler) | Informação é física ("it from bit") | Apagar 1 bit custa pelo menos k_B T ln 2 | Contexto |
| **Funcional (Hazen, Szostak et al.)** | **Raridade de configurações que cumprem uma função** | **I(E) = −log2 F(E)** | **Sim: base do projeto** |

## Ligação com o MIS

Para uma solução x, a função é ter energia H baixa: I_F(x) = −log2 (fração de y com H(y) ≤ H(x)). ⟨I_F⟩ é a média sob a distribuição do algoritmo. Em Hazen, F(E) conta configurações com função maior ou igual; no MIS minimizamos H, então contamos as com H menor ou igual. A ideia é a mesma.

## Por que não Shannon

A surpresa de Shannon mede quão improvável é x sob a distribuição do algoritmo. A informação funcional mede quão rara é x entre todas as configurações, em relação à função. Concentrar a distribuição não é o mesmo que concentrar em soluções boas.

## Fontes

As linhas de Shannon, Kolmogorov, Fisher e von Neumann/Holevo, e o custo de Landauer, são conhecimento de livro-texto, não conferido em fonte aberta. Conferidos nas páginas:

- Floridi, From data to semantic information: https://philarchive.org/archive/FLOFDT
- Bateson (Information Philosopher): https://informationphilosopher.com/solutions/scientists/bateson
- Hazen, informação funcional (Carnegie): https://hazen.carnegiescience.edu/node/8
- arXiv:0709.0612 (cita "it from bit" e "information is physical"): https://arxiv.org/pdf/0709.0612
