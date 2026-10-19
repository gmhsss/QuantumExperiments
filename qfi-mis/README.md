# QFI em MIS — Informação Funcional Quântica (PIBIC PUCPR)

Mede a informação funcional I_F(x) = -log2(|{y : H(y) <= H(x)}| / 2^n) sobre o espaço do problema
(Maximum Independent Set, H(x) = 2·Σ x_i x_j − Σ x_i) e compara algoritmos pelo ⟨I_F⟩ da distribuição que cada um produz.

## Estrutura
- `src/qfi_compare.py` — QAOA (p=1,2,3) vs EDAs (PBIL/UMDA) vs GA, mesma paisagem, eixo x = nº de avaliações. Gera `qfi_compare.png`.
- `src/qfi_qaoa_exact.py` — variante do QAOA com energia exata (limite superior).
- `src/qfi_bridge.py` — liga o código do David (enbpar-quantum-qaoa) à métrica; exige `PYTHONPATH=<repo do David>/src`.
- `src/qfi_mis_prototype.py` — protótipo n=8 com Qiskit.
- `docs/` — documento LaTeX/PDF com a formalização.
- `results/` — figura e tabela (xlsx).

## Uso
```
pip install -r requirements.txt
python src/qfi_compare.py        # ~3 min, n=14
python src/qfi_qaoa_exact.py
```

## Resultado preliminar (n=14, 3 grafos × 3 sementes)
Progresso normalizado de ⟨I_F⟩ (0 = uniforme, 1 = máximo), 150k avaliações:
EDAs ≈ 0,87; GA ≈ 0,5; QAOA p≤3 ≈ 0,13–0,27. Sem indício de vantagem quântica neste regime.

## n=20 (2 grafos × 2 sementes, 150 iterações COBYLA)
Mesmo padrão: UMDA/PBIL ≈ 0,86; GA ≈ 0,5–0,6; QAOA p=1/2/3 ≈ 0,09 / 0,15 / 0,26 (amostrado).
O QAOA melhora com a profundidade e com n, mas continua abaixo dos EDAs. Figura: `results/qfi_compare_n20.png`.
Rodar: `QFI_N=20 QFI_G=2 QFI_S=2 QFI_IT=150 python src/qfi_compare.py`.

## Validação
`src/validate_qaoa.py`: simulador numpy do QAOA vs Qiskit (RZ/RZZ/RX), diferença máxima de probabilidades 2e-16.

## Limitações / pendências
- Falta n≈25 (statevector de 33M estados é pesado; precisa de GPU/MPS). n=20 feito com poucas sementes.
- Contagem de amostras favorece energia exata; EDAs saturam por clipping [0,02; 0,98].
