# Conversa Histórica: Branch · Oportunidades para Devs Solidity

- **Projeto / Subdomínio:** `03_printintel`
- **Data:** `2026-07-02`
- **ID:** `6a45d75b-f1e0-83e9-b89a-aeb2d114408e`
- **Total de Mensagens:** 48

---

### 👤 USUÁRIO *(22:47:29 UTC)*:

Estou há alguns anos (uns 4~5) sem mexer com blockchain e solidity. Queria saber o que tem de novo no setor, quais oportunidades de novos negócios existem para devs solidity e o que tem mudado no cenário geral em blockchain

---

### 🤖 ASSISTENTE (ChatGPT) *(22:47:29 UTC)*:

Vou te dar uma visão prática, pensando como dev que já conhece Solidity: primeiro o que mudou tecnicamente, depois onde há oportunidade real de produto/negócio e, por fim, como se reposicionar sem tentar “aprender tudo de novo”.

---

### 🤖 ASSISTENTE (ChatGPT) *(22:48:19 UTC)*:

Primeira conclusão já aparece bem clara: o setor ficou menos “ICO/NFT hype” e mais infraestrutura financeira. Stablecoins, L2s, tokenização, segurança e integração com sistemas tradicionais viraram temas bem mais importantes do que lançar token por lançar.

---

### 🤖 ASSISTENTE (ChatGPT) *(22:48:44 UTC)*:

Sim — mudou bastante. A principal diferença é que blockchain saiu de uma fase mais “token/NFT/metaverso/DeFi selvagem” e entrou em uma fase mais **infraestrutura financeira, UX, L2, stablecoins, compliance, tokenização e segurança**.

## Resumo direto

Hoje, para um dev Solidity, as melhores oportunidades não estão em “criar mais um token”, mas em construir **infraestrutura útil em cima de EVM**: pagamentos com stablecoins, automação financeira, tokenização de ativos, integrações DeFi, wallets melhores, auditoria/segurança, indexação on-chain, compliance e produtos para L2s.

Ethereum também mudou bastante: Dencun trouxe blobs/EIP-4844 em 2024; Pectra ativou EIP-7702 em 2025, permitindo EOAs com funcionalidades de smart accounts, como batching, gas sponsorship, autenticação alternativa e spending controls; e Fusaka, em dezembro de 2025, trouxe PeerDAS para escalar blobs e reduzir pressão de dados nos nós. citeturn668416view2turn668416view4

## O que tem de novo tecnicamente

**1. Ethereum virou “L1 de liquidação + L2s para uso real”.**  
A narrativa de hoje é rollup-centric: Arbitrum, Base, OP Mainnet, ZKsync, Starknet, Linea, Mantle, Unichain etc. L2BEAT lista dezenas de soluções, com 22 rollups, 6 validiums/optimiums e outros projetos; Arbitrum One e Base aparecem entre os maiores, com bilhões de dólares em valor protegido. citeturn467815view0

**2. Account abstraction deixou de ser só buzzword.**  
Com EIP-7702 em Pectra, uma carteira comum pode ganhar temporariamente comportamento de smart contract. Na prática, isso abre espaço para UX melhor: transação patrocinada, pagamento de gas com outro token, múltiplas ações em uma transação, passkeys, limites de gasto, recuperação social e wallets mais próximas de apps Web2. citeturn668416view2

**3. Solidity e tooling amadureceram muito.**  
Se você parou há 4–5 anos, provavelmente usava Hardhat/Truffle. Hoje, **Foundry** virou padrão forte para projetos sérios; a pesquisa oficial de Solidity 2025 mostra Foundry como framework dominante, usado por 57% dos respondentes, enquanto Truffle praticamente desapareceu. A mesma pesquisa mostra que 88% usam ferramentas de IA pelo menos mensalmente, mas 45% ainda desconfiam da saída da IA — ou seja, IA ajuda, mas não substitui revisão técnica/auditoria. citeturn668416view0

**4. Solidity ganhou recursos e mudanças relevantes.**  
Nos últimos anos entraram coisas como custom errors em `require`, suporte a transient storage/EIP-1153, melhorias no pipeline via-IR, storage layouts customizados, suporte a novas versões de EVM e, em 0.8.35, builtin para ERC-7201 em padrões upgradeáveis. citeturn258005view1turn258005view0

**5. DeFi ficou mais modular.**  
Uniswap v4, lançado em 2025, trouxe hooks e arquitetura singleton, permitindo pools com lógica customizada: taxas dinâmicas, ordens on-chain, estratégias de liquidez, restrições, automações e integrações com RWAs/compliance. Isso é uma área excelente para devs Solidity mais avançados. citeturn718573search1turn718573search9

## O que mudou no cenário geral

A maior mudança é: **stablecoins viraram o principal caso de uso real**. O relatório State of Crypto 2025 da a16z aponta stablecoins com US$ 46 trilhões em volume anual total e US$ 9 trilhões em volume ajustado, além de mais de US$ 300 bilhões em supply. Mesmo com viés pró-cripto da fonte, o sinal é forte: pagamentos, remessas, tesouraria e liquidação estão puxando adoção. citeturn668416view1

Também houve entrada pesada de instituições. Visa, BlackRock, Fidelity, JPMorgan, PayPal, Stripe, Robinhood e outras passaram a oferecer, integrar ou planejar produtos cripto; fintechs e instituições estão criando infra própria para pagamentos, stablecoins e ativos tokenizados. citeturn668416view1

Outro movimento grande é **tokenização de ativos do mundo real**, os famosos RWAs: fundos, títulos, recebíveis, imóveis, crédito privado, commodities e ativos financeiros representados on-chain. A oportunidade aqui não é só o contrato ERC-20; é todo o stack: emissão, custódia, whitelist/KYC, compliance, distribuição, liquidação, relatórios, prova de reserva, contabilidade e integração com sistemas legados. A CVM no Brasil mantém sandbox regulatório para modelos inovadores e lista benefícios como redução de custos, aumento de segurança jurídica e teste supervisionado de novos modelos. citeturn974717view1

## Oportunidades de negócio para devs Solidity

**1. Auditoria e segurança de smart contracts**  
Essa talvez seja a oportunidade mais sólida. Quanto mais capital institucional entra, mais caro fica errar. Auditoria, fuzzing, invariant testing, formal verification, monitoramento on-chain, detecção de ataques e ferramentas internas para equipes DeFi são áreas muito valorizadas. Relatórios recentes de segurança apontam que auditoria isolada já não basta; risco operacional, chaves, permissões, bridges, oráculos e governança viraram parte central da superfície de ataque. citeturn826665search1

**2. Stablecoin payments**  
Produtos possíveis: checkout com USDC/USDT, payroll internacional, remessas, split de pagamento, liquidação B2B, tesouraria, conciliação, pagamento para freelancers e integração com Pix/contabilidade. O valor está menos em “criar a stablecoin” e mais no **plumbing**: wallets, compliance, APIs, accounting, custody, chargebacks alternativos e experiência de usuário. Reuters também destacou que a oportunidade de longo prazo está na infraestrutura por trás das stablecoins, como processadores, carteiras, custódia e compliance. citeturn389700news78

**3. Tokenização/RWA para mercados locais**  
No Brasil, eu olharia com carinho para recebíveis, crédito privado, contratos, garantias, consórcios, precatórios, imóveis fracionados e ativos de nicho. Mas aqui você precisa trabalhar junto com jurídico/regulatório. O dev Solidity que entende **CVM, Bacen, KYC, custody, permissioned tokens, ERC-3643/1400-like patterns, whitelists e governança** fica bem mais valioso.

**4. Account abstraction e smart wallets**  
Aqui entram carteiras com passkeys, gasless transactions, sessão temporária para apps, limites de gasto, recuperação social, carteiras para empresas, carteiras para IA agents e carteiras para usuários não técnicos. Com EIP-7702, isso ficou muito mais interessante para builders EVM. citeturn668416view2

**5. DeFi tooling e automação**  
Não necessariamente criar mais um protocolo DeFi, mas ferramentas em volta: rebalanceamento, gestão de liquidez, dashboards de risco, automação de vaults, simulação de liquidação, monitoramento de posições, alertas de governança, ferramentas para LPs de Uniswap v4, hooks e estratégias customizadas.

**6. Infra para L2s e appchains**  
Muita empresa quer usar blockchain sem lidar com L1 caro. Oportunidades: deploy em Base/Arbitrum/Optimism, bridges mais seguras, indexadores, sequencer monitoring, relayers, ferramentas cross-chain, SDKs, dashboards, integração com oráculos, provas e data availability.

**7. Compliance/on-chain analytics**  
Instituições precisam saber de onde veio o dinheiro, risco de wallet, sanções, lavagem, exposição a hacks, proof of reserves e relatórios. Dev Solidity + backend + dados on-chain é um perfil forte aqui.

**8. IA + blockchain**  
Ainda tem hype, mas há casos reais surgindo: agentes de IA com wallets, pagamentos autônomos por API/compute, permissões on-chain, logs auditáveis, provas de execução, reputação e identity/delegation. Ethereum.org já trata AI agents como uma categoria de uso em Ethereum, e Chainalysis descreve a convergência como IA decidindo/automatizando e blockchain executando/registrando de forma transparente. citeturn972712search14turn972712search10

## Onde eu não perderia tempo

Eu evitaria começar por:

Tokens meme sem utilidade;  
NFT PFP genérico;  
“metaverso” sem distribuição;  
DAO só de governança cosmética;  
fork de DEX/lending sem vantagem clara;  
bridge própria sem equipe de segurança pesada;  
qualquer projeto que dependa de tokenomics para mascarar falta de produto.

## Stack que eu reaprenderia hoje

Para voltar bem ao mercado, eu focaria nisso:

**Base Solidity moderna:** Solidity 0.8.24+, custom errors, transient storage, upgradeable contracts, proxies, storage layout, ERC-7201, EIP-712, permits, ERC-4626, ERC-1155/6909, ERC-4337/7702.

**Tooling:** Foundry, Forge, Cast, Anvil, Hardhat só quando necessário, OpenZeppelin, Solmate/Solady com cuidado, Slither, Echidna, Medusa, Mythril, Tenderly, Etherscan verification, Sourcify.

**Web3 app layer:** TypeScript, viem, wagmi, RainbowKit, Safe, Privy, Dynamic, WalletConnect, subgraphs/indexers, The Graph, Goldsky, Ponder.

**Security:** fuzzing, invariant tests, differential tests, reentrancy moderna, oracle manipulation, MEV, flash loans, governance attacks, upgrade risk, bridge risk, access control, timelocks.

**L2s:** Base, Arbitrum, Optimism/OP Stack, Polygon CDK, ZKsync, Linea, Starknet se quiser aprender Cairo, e noções de data availability/blobs.

## Como eu me reposicionaria em 60 dias

Semana 1–2: atualizar Solidity/Foundry e refazer padrões clássicos: ERC-20, ERC-721, ERC-4626 vault, proxy upgradeável, permit/EIP-712.  
Semana 3–4: construir um projeto real em uma L2, por exemplo um checkout com USDC + dashboard + eventos indexados.  
Semana 5: adicionar account abstraction/gas sponsorship ou smart wallet flow.  
Semana 6: fuzzing, invariants, Slither, relatório de segurança e documentação técnica.  
Semana 7–8: publicar como portfólio: contrato verificado, testes, threat model, post técnico e demo.

O projeto ideal para portfólio seria algo como:

**“Stablecoin Payroll / Split Payments on Base”**  
Com USDC, permissões, limites de gasto, assinatura EIP-712, painel de pagamentos, eventos indexados, testes com Foundry, fuzzing, documentação de riscos e integração front-end.

Isso mostra muito mais maturidade do que “criei um token”.

## Mercado de trabalho

Ainda existe demanda para Solidity, mas a régua subiu. Vagas boas pedem segurança, DeFi primitives, L2, backend, TypeScript e capacidade de escrever testes sérios. Dados de sites de vagas Web3 variam bastante, mas aparecem faixas globais de Solidity entre algo como US$ 65k–257k/ano em Web3.career e média global menor em CryptoJobsList; eu trataria esses números como referência de mercado remoto, não garantia. citeturn113066search2turn113066search5

Minha leitura: **Solidity puro júnior está mais difícil; Solidity + segurança + produto financeiro + backend está muito bom**.

## Minha aposta prática

Se você quer voltar para blockchain com chance real de negócio, eu priorizaria nesta ordem:

1. **Stablecoins e pagamentos B2B/B2C**
2. **Tokenização/RWA com compliance**
3. **Auditoria, segurança e monitoramento**
4. **Account abstraction/smart wallets**
5. **Ferramentas DeFi para L2s**
6. **IA agents com wallets e permissões on-chain**

Para o seu perfil de dev backend/Java/AWS, você não precisa virar “cripto degen”. Sua vantagem pode ser justamente o contrário: construir **infra confiável, testada, observável e integrável com sistemas tradicionais**. Esse é o tipo de perfil que o setor passou a valorizar mais.

navlistDesenvolvimentos recentes para acompanharturn389700news78,turn389700news79,turn315327news37,turn315327news38

---

### 👤 USUÁRIO *(23:29:25 UTC)*:

Quero oportunidade de ganhar dinheiro em projeto solo

---

### 🤖 ASSISTENTE (ChatGPT) *(23:29:25 UTC)*:

Vou focar em oportunidades “solo-friendly”: baixo custo inicial, escopo pequeno, possível vender para empresas/devs ou monetizar como ferramenta/SaaS, sem depender de captar investimento nem montar protocolo gigante.

---

### 🤖 ASSISTENTE (ChatGPT) *(23:29:44 UTC)*:

Para **projeto solo**, eu evitaria criar “mais um protocolo” e focaria em algo que venda para **devs, pequenas empresas, fintechs, contadores, creators ou times Web3**. Minha recomendação principal para você seria:

# Melhor oportunidade: micro-SaaS de pagamentos com stablecoin

Construir uma ferramenta simples para **cobrança, split, recibo e conciliação de pagamentos em USDC/USDT em L2**, começando por Base/Arbitrum/Optimism.

O motivo: stablecoins viraram um dos casos de uso mais fortes de blockchain. Há movimento institucional pesado: Visa, Mastercard, Coinbase e outras empresas anunciaram uma iniciativa de stablecoin global chamada Open USD em 30 de junho de 2026, e BNY também passou a integrar USDC em sua plataforma de ativos digitais. citeturn932573news51turn932573news54

No Brasil, o tema também ficou mais sério: o Banco Central publicou regras para prestadores de serviços de ativos virtuais, incluindo exigências de autorização, proteção ao consumidor, governança, controles internos, segurança e PLD/FT; transações com ativos virtuais pareados a moeda fiduciária, como stablecoins, também passaram a ser tratadas com atenção regulatória especial. citeturn841039news27turn841039search0

## O produto

Algo como:

**PayFlow Crypto BR**  
Um micro-SaaS para freelancers, dev shops, agências, infoprodutores e pequenos negócios receberem em stablecoin com:

- link de pagamento;
- invoice em dólar;
- QR/link de carteira;
- split automático entre sócios;
- dashboard de recebimentos;
- exportação CSV/Excel para contador;
- cálculo de cotação BRL/USD no dia;
- webhook/API para integrar com sistemas;
- alerta de pagamento confirmado;
- recibo simples;
- suporte a Base inicialmente.

Você não precisa virar banco, exchange ou custodiante. O MVP pode ser **non-custodial**, apenas gerando cobrança, monitorando eventos on-chain e organizando conciliação. Isso reduz muito a complexidade regulatória inicial, embora ainda valha validar com advogado antes de vender agressivamente no Brasil.

## Por que isso é bom para solo dev

Porque você consegue construir sozinho:

Backend + frontend + indexador + smart contracts simples + integração com wallet.

Você não precisa ter liquidez, market maker, token próprio, comunidade gigante ou VC. O dinheiro vem de assinatura.

Exemplo de monetização:

- plano grátis: até 5 cobranças/mês;
- plano Pro: R$ 49–99/mês;
- plano Business: R$ 199–499/mês;
- setup personalizado para empresa: R$ 1.000–5.000;
- taxa opcional por volume, se o modelo regulatório permitir.

O diferencial não é “pagar em cripto”. É **resolver a dor chata de quem recebe em stablecoin e depois precisa entender quem pagou, quanto, quando, em qual cotação, qual invoice, qual cliente e como explicar isso para contabilidade**.

# Ranking de oportunidades solo

## 1. Dashboard de conciliação stablecoin para freelancers e PMEs

Esse é o mais promissor.

Você faz o usuário cadastrar uma carteira, e o sistema lê entradas de USDC/USDT, agrupa por cliente, gera relatório mensal, exporta CSV/Excel e emite recibo/invoice.

**MVP em 30 dias:**
- login;
- cadastro de wallets;
- leitura de transações USDC na Base;
- dashboard;
- exportação CSV;
- cadastro manual de cliente;
- webhook de pagamento.

**Stack:**
Solidity quase mínimo, talvez nenhum contrato no começo.  
Backend: Python/FastAPI ou Java/Spring.  
On-chain: viem/ethers, Alchemy/QuickNode, Basescan API ou indexador próprio.  
Front: Next.js.

**Como ganha dinheiro:** assinatura mensal.

Essa é a oportunidade mais “pé no chão”.

---

## 2. Ferramenta de auditoria leve para contratos Solidity

Criar um produto que rode uma bateria de análise em repositórios Solidity:

- Slither;
- Foundry tests;
- coverage;
- checklist OWASP/SCSVS;
- detecção de padrões perigosos;
- análise de permissões/admin;
- relatório em PDF/Markdown;
- sugestões de testes fuzz/invariant.

A segurança continua sendo uma das áreas com dinheiro real. A Immunefi lista 210 bounties ativos e programas com recompensas relevantes; por exemplo, há programas com críticos de US$ 100 mil, US$ 250 mil ou até mais, dependendo do protocolo. citeturn932573search4turn932573search5turn932573search17turn932573search22

**Produto solo possível:**  
“GitHub Action para segurança Solidity + relatório bonito”.

**Cliente:**  
projetos pequenos que não conseguem pagar auditoria grande, mas querem uma pré-auditoria automatizada antes de contratar auditoria formal.

**Monetização:**
- SaaS por repositório;
- relatório avulso por R$ 300–1.500;
- consultoria/auditoria leve;
- upsell para revisão manual.

Essa combina muito bem com portfólio e autoridade técnica.

---

## 3. Gerador de contratos tokenizados com compliance básico

Uma plataforma para gerar contratos de tokenização com:

- whitelist;
- roles;
- pause;
- transfer restrictions;
- cap table;
- snapshots;
- burn/mint controlado;
- relatórios;
- documentação automática;
- templates ERC-20/721/1155/3643-like.

A CVM mantém sandbox regulatório para testar inovações no mercado de capitais com autorização temporária e supervisionada, e o tema tokenização segue ativo no Brasil. citeturn841039search7turn841039search4

Aqui, o cuidado é: **não venda como solução regulatória pronta**. Venda como ferramenta técnica para advogados, fintechs, tokenizadoras e empresas estruturarem POCs.

**Monetização:**
- licença por projeto;
- geração de contrato + deploy;
- consultoria técnica;
- documentação técnica para jurídico.

É mais B2B, ticket maior, ciclo de venda mais lento.

---

## 4. Bot de monitoramento on-chain para empresas

Um produto que monitora:

- recebimentos;
- grandes transferências;
- permissões perigosas;
- alteração de owner/admin;
- eventos de contrato;
- carteira recebendo de endereço suspeito;
- mudança em contrato proxy;
- saldo baixo;
- tentativa de interação com contrato conhecido como malicioso.

Pode ser vendido como “Datadog/Sentry para carteiras e contratos”.

**MVP:**
- cadastrar wallet/contrato;
- escolher rede;
- configurar alertas;
- enviar alerta por Telegram/Discord/Slack/e-mail;
- painel simples.

**Monetização:**
- R$ 49–499/mês;
- planos por quantidade de wallets/contratos;
- setup personalizado.

Esse projeto é excelente para solo porque pode começar simples e ficar cada vez mais sofisticado.

---

## 5. Templates pagos para Foundry + Solidity moderno

Você cria kits prontos:

- ERC-4626 vault template;
- ERC-20 com permit;
- contrato upgradeável com ERC-7201;
- template de invariant testing;
- template de deploy multi-chain;
- Uniswap v4 hook starter;
- account abstraction starter;
- stablecoin checkout starter.

A pesquisa oficial de Solidity 2025 mostrou Foundry como framework dominante entre respondentes, com 57% de uso, então vender educação, templates e ferramentas ao redor de Foundry faz sentido. citeturn932573search2

**Monetização:**
- Gumroad/Lemon Squeezy;
- curso curto;
- assinatura de templates;
- consultoria de setup.

Não é o maior teto financeiro, mas é ótimo para construir audiência.

---

## 6. Bug bounty como renda variável

Isso não é exatamente “produto”, mas pode gerar dinheiro enquanto você constrói autoridade.

Caminho:
- estudar exploits famosos;
- resolver CTFs como Ethernaut, Damn Vulnerable DeFi, Paradigm CTF;
- participar de Sherlock, Code4rena, Cantina, Immunefi;
- publicar writeups;
- transformar aprendizados em ferramenta/consultoria.

A vantagem: você aprende segurança real.  
A desvantagem: renda irregular, muita competição e muito falso positivo.

Eu usaria como **estratégia paralela**, não como único plano.

# O que eu faria no seu lugar

Pelo seu perfil de backend/Java/AWS e interesse em projeto solo, eu escolheria um destes dois caminhos:

## Caminho A — mais comercial

**Micro-SaaS de conciliação e cobrança em stablecoin.**

É o melhor equilíbrio entre produto, demanda, escopo solo e monetização recorrente.

Nome conceitual:

**StableDesk**  
“Receba em stablecoin, concilie como empresa.”

MVP:

1. usuário conecta ou cadastra wallet;
2. cria cliente;
3. gera invoice;
4. sistema monitora pagamento;
5. mostra status;
6. exporta relatório mensal;
7. envia webhook/e-mail;
8. cobra assinatura.

Você pode começar sem contrato próprio. Depois adiciona smart contracts para split, escrow ou recorrência.

## Caminho B — mais técnico e valorizado

**Security Scanner / Audit Assistant para Solidity.**

Nome conceitual:

**ForgeGuard**  
“Pré-auditoria automática para projetos Solidity.”

MVP:

1. usuário conecta GitHub;
2. ferramenta roda Slither + Foundry;
3. detecta problemas comuns;
4. gera relatório;
5. sugere testes;
6. cria checklist de riscos;
7. exporta PDF/Markdown.

Esse caminho pode virar SaaS, consultoria, curso e autoridade.

# Minha recomendação final

Eu começaria com o **StableDesk**, porque tem uma dor de negócio mais clara.

Versão 1 não precisa ser “cripto revolucionária”. Precisa ser útil:

> “Cole sua wallet, gere cobranças em USDC na Base, acompanhe pagamentos e baixe um relatório organizado para contabilidade.”

Isso já é vendável.

Depois você expande:

- split entre sócios;
- cobrança recorrente;
- assinatura com stablecoin;
- escrow;
- checkout para e-commerce;
- API para devs;
- Pix + stablecoin, com cuidado regulatório;
- integração contábil;
- multi-chain;
- detecção de risco de wallet.

# Plano de MVP em 4 semanas

## Semana 1 — Infra e leitura on-chain

- Criar app Next.js ou frontend simples.
- Backend FastAPI/Spring.
- Login.
- Cadastro de wallet.
- Leitura de entradas USDC na Base.
- Salvar transações no banco.

## Semana 2 — Invoices

- Criar invoice.
- Gerar link público.
- Mostrar valor em USD e BRL.
- Associar pagamento recebido à invoice.
- Status: aguardando, pago, expirado, divergente.

## Semana 3 — Relatórios

- Dashboard mensal.
- Exportação CSV/XLSX.
- Filtro por cliente.
- Cotação do dia.
- Recibo simples em PDF.

## Semana 4 — Monetização

- Stripe/Mercado Pago para assinatura fiat.
- Plano grátis e Pro.
- Landing page.
- Demo pública.
- 10 usuários beta.

# Funcionalidades que eu deixaria fora no começo

Não comece com:

- emissão de token próprio;
- bridge própria;
- custódia de fundos;
- cartão cripto;
- conversão automática para real;
- promessa de rendimento;
- marketplace financeiro;
- tokenização de ativo real;
- KYC completo;
- integração bancária complexa.

Tudo isso aumenta muito o risco técnico, jurídico e operacional.

# Primeiro cliente ideal

Não tente vender para banco.

Venda para:

- dev freelancer que recebe de fora;
- agência pequena;
- consultor Web3;
- criador de conteúdo;
- comunidade paga;
- software house;
- empresa que paga colaboradores internacionais;
- projeto cripto pequeno que precisa organizar tesouraria.

A copy da landing page poderia ser:

:::writing{variant="document" id="48392"}
Receba pagamentos em stablecoin sem perder o controle financeiro.

Gere cobranças em USDC, acompanhe pagamentos na blockchain, organize clientes e exporte relatórios mensais para sua contabilidade. Ideal para freelancers, agências e pequenos negócios que recebem em dólar digital.
:::

# Como validar antes de codar tudo

Faça uma landing page simples com:

- “Conciliação de pagamentos USDC para freelancers e empresas”
- campo de e-mail;
- botão “Quero testar”
- print fake do dashboard;
- 3 planos.

Depois poste em:

- LinkedIn;
- grupos de devs;
- comunidades Web3 Brasil;
- Discords de Base/Optimism/Arbitrum;
- Reddit;
- grupos de freelancers;
- comunidades de nômades digitais.

Meta inicial: **10 pessoas conversando com você**. Se 3 disserem “eu pagaria por isso”, constrói.

# Veredito

A oportunidade solo mais realista hoje é:

**Um micro-SaaS B2B simples, sem custódia, para cobrança, conciliação e relatórios de pagamentos em stablecoin.**

É pequeno o suficiente para você construir sozinho, útil o suficiente para alguém pagar, e conectado com uma tendência forte do mercado: stablecoins virando infraestrutura de pagamento.

navlistNotícias recentes para acompanhar stablecoins e regulaçãoturn932573news51,turn932573news54,turn841039news27

Dá para monitorar novas grants, hackathons e oportunidades de bounty para Solidity/Base/Optimism e te avisar quando aparecer algo bom.

---

### 👤 USUÁRIO *(01:01:09 UTC)*:

Existe alguma forma de rodar contratos inteligentes com monero ou outra privacy coin? Alguma nova crypto relevante deste tipo saiu no mercado

---

### 🤖 ASSISTENTE (ChatGPT) *(01:01:39 UTC)*:

Sim, existe — mas **não do jeito “rodo Solidity dentro do Monero”**.

## 1. Monero tem smart contracts?

**Monero, nativamente, não é uma plataforma de smart contracts generalistas.** Ele foi desenhado para ser dinheiro privado: transferências com privacidade por padrão, escondendo remetente, destinatário e valor. A própria página oficial posiciona Monero como uma moeda para pagamentos privados, não como uma L1 programável tipo Ethereum. citeturn192900search0

O que existe no ecossistema Monero é mais nesta linha:

- **atomic swaps BTC/XMR**;
- pesquisas e implementações de **ETH/XMR atomic swaps**;
- DEXs P2P como Haveno/BasicSwap;
- projetos como Serai tentando criar DEX cross-chain com suporte a XMR;
- uso de XMR como camada de privacidade/settlement, não como runtime de contratos.

Atomic swaps com Monero são reais: o próprio GetMonero explica swaps BTC↔XMR como troca sem terceiro confiável. Para ETH↔XMR, houve proposta financiada pela comunidade Monero para conectar a blockchain de smart contracts Ethereum ao Monero via atomic swap. citeturn900073search0turn900073search3

A limitação é que Monero não tem scripting/HTLC como Bitcoin/Ethereum. Um paper de 2025 sobre DEXs P2P no ecossistema Monero observa justamente que HTLCs dependem de capacidades de scripting indisponíveis no Monero, o que obriga soluções criptográficas mais específicas. citeturn900073search11

**Resumo:** com Monero você consegue fazer pagamentos privados e swaps, mas não construir dApps complexos diretamente na chain como faria com Solidity.

---

# 2. Dá para usar Monero junto com smart contracts?

Sim, de algumas formas.

## A. Atomic swap ETH/XMR

Você pode ter um contrato no Ethereum/Base/Arbitrum de um lado e uma transação Monero do outro. O contrato não “controla” Monero como controla ERC-20, mas o protocolo de swap garante que a troca ocorra ou seja revertida.

Uso possível:

- vender acesso a um serviço com pagamento em XMR;
- trocar XMR por stablecoin/ETH;
- criar fluxo de pagamento privado com liquidação externa;
- usar XMR como “privacy off-ramp” de um app EVM.

Mas para um projeto solo, isso é tecnicamente mais chato do que parece. ETH/XMR atomic swap envolve criptografia, UX difícil, liquidez e risco de implementação. A implementação AthanorLabs existe, mas se descreve como beta. citeturn900073search14

## B. Wrapped XMR em EVM

Outra opção é usar algum **wXMR** em Ethereum ou outra EVM. Aí você consegue usar Solidity normalmente.

Problema: quase sempre você troca a privacidade nativa do Monero por um token representativo em uma chain pública. Dependendo do bridge/custódia, você ganha composabilidade, mas perde boa parte da tese de privacidade.

## C. Usar Monero como pagamento externo

Para projeto solo, talvez seja o caminho mais prático:

- app off-chain gera invoice em XMR;
- monitora pagamento com view key;
- libera acesso/serviço;
- usa smart contracts apenas em outra chain quando fizer sentido.

Isso não é “smart contract com Monero”, mas pode ser um produto real: gateway privado de pagamentos, assinatura, marketplace ou cobrança B2B com privacidade.

---

# 3. Privacy coins/chains com smart contracts

Aqui está o mapa prático.

## Melhor opção para quem vem de Solidity: Oasis Sapphire

**Oasis Sapphire** é provavelmente o caminho mais direto para você, porque é **EVM-compatible** e permite contratos confidenciais. A documentação oficial diz que Sapphire é o ParaTime confidencial da Oasis para desenvolvimento de smart contracts com compatibilidade EVM. citeturn192900search5

Isso significa que você pode escrever algo parecido com Solidity/Ethereum, mas com recursos de confidencialidade para inputs, estado ou outputs dependendo do design.

Casos bons:

- leilão privado;
- votação privada;
- jogo com informação escondida;
- sealed-bid auction;
- payroll confidencial;
- KYC/score privado;
- contratos B2B com valores não públicos;
- randomização on-chain com sigilo.

**Para projeto solo:** é a melhor ponte entre seu conhecimento antigo de Solidity e o mundo de privacy smart contracts.

---

## Secret Network

**Secret Network** é uma L1 do ecossistema Cosmos focada em smart contracts privados. O site oficial fala em “smart contracts built for privacy” e contratos que protegem dados de usuários. citeturn192900search1

A diferença é que você não usa Solidity; normalmente trabalha com **CosmWasm/Rust**. A privacidade vem de execução em ambientes confiáveis, como TEEs/Intel SGX, e não só de ZK. Isso traz vantagens de performance e flexibilidade, mas também uma premissa de confiança diferente.

Casos bons:

- dados sensíveis em dApps;
- permissões privadas;
- NFTs com metadados privados;
- apps de saúde/dados pessoais;
- jogos com estado oculto;
- private DeFi mais customizado.

**Para projeto solo:** bom se você topar aprender Cosmos/CosmWasm. Menos direto que Sapphire para quem quer reaproveitar Solidity.

---

## Aleo

**Aleo** é uma das apostas mais relevantes de “programmable privacy” com zero-knowledge. A tese é permitir aplicações privadas por padrão usando ZK, com linguagem própria chamada **Leo**. O site oficial posiciona Aleo como blockchain para aplicações privadas e pagamentos privados/compliance. citeturn452941search9

O mainnet da Aleo foi lançado em 2024, e fontes do ecossistema trataram o lançamento como um marco importante para privacidade programável. citeturn452941search3

Casos bons:

- identidade privada;
- proof of income sem expor renda;
- KYC seletivo;
- jogos com estado privado;
- pagamentos privados;
- compliance com selective disclosure;
- credenciais verificáveis.

**Para projeto solo:** tecnicamente interessante, mas você vai aprender um stack novo. Melhor para produtos ZK-nativos do que para portar um app Solidity.

---

## Aztec

**Aztec** é um dos projetos mais importantes para privacidade programável no Ethereum. A documentação define Aztec como uma L2 zkRollup privacy-first que traz privacidade para smart contracts, transações confidenciais e estado privado; também deixa claro que **não é EVM-compatible**. citeturn530510search8

Em 2026, apareceram notícias sobre lançamento de Alpha/Mainnet, mas com ressalvas fortes: reportagens apontaram que a Alpha era experimental e mencionaram vulnerabilidades conhecidas/patches planejados. citeturn192900search25

Casos bons:

- DeFi privado;
- identidade privada;
- voting/governance privado;
- wallets com privacidade;
- dApps Ethereum com estado confidencial.

**Para projeto solo:** muito promissor, mas eu trataria como tecnologia de fronteira. Bom para estudar e fazer POC, mas ainda arriscado para produto comercial imediato.

---

## Dero

**Dero** é uma privacy coin/L1 que promete combinar privacidade e smart contracts. A documentação oficial descreve DERO como blockchain em Go com foco em privacidade aprimorada e smart contracts. citeturn530510search0

O ponto fraco é ecossistema. É bem menor que Ethereum/Oasis/Aztec/Aleo/Secret. Pode ser interessante tecnicamente, mas para ganhar dinheiro solo eu teria cautela: menos usuários, menos liquidez, menos tooling, menos clientes.

**Para projeto solo:** só escolheria se você quiser apostar em nicho hardcore de privacy coin.

---

## Railgun

**Railgun** não é exatamente uma “privacy coin L1”; é um protocolo de privacidade em smart contracts sobre chains existentes. A página da Ethereum.org descreve Railgun como sistema on-chain que usa zero-knowledge para permitir uso privado de smart contracts e DeFi sem sair da segurança da chain escolhida. citeturn530510search13

Isso é interessante porque você continua no ecossistema EVM, mas adiciona uma camada de privacidade para DeFi.

Casos bons:

- private swaps;
- private balances;
- uso de DeFi sem expor wallet principal;
- integração de privacidade em wallets;
- shielding/unshielding de assets.

**Para projeto solo:** pode render ferramentas, dashboards, integrações e automações, mas é uma área sensível regulatoriamente.

---

## Namada e Penumbra

**Namada** e **Penumbra** são mais focadas em **shielded assets/interchain privacy** do que em “Solidity privado”.

Namada completou seu mainnet em 2025 e permite proteger múltiplos ativos, inicialmente no ecossistema IBC/Cosmos. citeturn452941search10

Penumbra se apresenta como uma rede proof-of-stake e DEX cross-chain totalmente privada, permitindo shieldar ativos IBC e transacionar, fazer staking, swaps e market making sem expor informação pessoal. citeturn530510search26

**Para projeto solo:** mais interessante para produto de trading privado, DEX, analytics, wallet, bridge UX ou tooling Cosmos do que para smart contracts Solidity.

---

## Zcash

**Zcash** continua relevante como privacy coin, mas não é uma plataforma generalista de smart contracts tipo Ethereum. O movimento mais interessante é **Zcash Shielded Assets**, descrito nos ZIPs 226 e 227, que propõem emissão, transferência e burn de custom assets dentro do protocolo Orchard. citeturn286807search2turn286807search5

Isso pode aproximar Zcash de um ecossistema de ativos privados, mas ainda não é “rodo Solidity privado no Zcash”.

**Para projeto solo:** eu olharia mais para wallets, pagamentos, tooling, relatórios e integrações do que para dApps complexos.

---

# 4. Alguma crypto nova/relevante desse tipo saiu?

Sim. As mais relevantes para acompanhar hoje são:

## Aleo

Provavelmente a mais relevante entre as novas L1s de privacidade programável. Tem mainnet, linguagem própria, foco em ZK e uma tese clara de private apps.

## Aztec

Não é “coin clássica” no mesmo sentido de Monero, mas é muito relevante porque tenta trazer privacidade programável para o ecossistema Ethereum. Só que ainda é fronteira/experimental.

## Namada

Relevante para **shielded assets interchain**, especialmente Cosmos/IBC. Menos “smart contracts”, mais “pool de privacidade multiativo”.

## Penumbra

Relevante para **private DEX/trading/staking** no Cosmos. Muito interessante como conceito, mas nichado.

## Railgun

Relevante como protocolo EVM de privacidade para DeFi. Não é uma L1 nova, mas talvez seja uma das opções mais práticas para integrar privacidade em apps EVM.

## Oasis Sapphire

Não é nova, mas é uma das mais práticas para dev Solidity porque entrega EVM confidencial em produção.

---

# 5. Minha recomendação para você

Como você vem de Solidity e está pensando em **projeto solo para ganhar dinheiro**, eu ordenaria assim:

## 1. Oasis Sapphire

Melhor para construir rápido com mentalidade Solidity.

Ideia de produto:

> **Private B2B Escrow / Sealed Bid Quotes**  
> Empresas fazem propostas, leilões ou cotações com valores privados. O contrato define vencedor/regras sem expor todos os lances publicamente.

Isso é vendável para B2B, compras, freelas, RFQ, licitação privada, marketplaces e negociação.

## 2. Railgun tooling

Não construir outro Railgun, mas construir algo em volta:

- dashboard de private DeFi;
- ferramenta de compliance com selective disclosure;
- wallet UX;
- alertas;
- relatórios;
- accounting para interações privadas.

## 3. Aleo

Boa aposta se você quiser aprender ZK de verdade e criar algo mais diferenciado.

Ideia:

> **Proof-of-income / proof-of-balance sem revelar saldo**  
> Usuário prova que tem renda, saldo, elegibilidade ou reputação sem expor dados brutos.

## 4. Monero payment infra

Mais pé no chão:

> **Gateway de assinatura/pagamento em XMR para SaaS, creators e comunidades.**

Você não roda smart contract no Monero, mas usa a privacidade dele como feature real. Pode usar view keys para conciliação e liberar acesso off-chain.

---

# 6. O que eu não faria

Eu não começaria por:

- criar uma nova privacy coin;
- fazer bridge própria XMR↔EVM;
- lançar token privado;
- prometer anonimato absoluto;
- construir mixer;
- criar ferramenta para burlar compliance;
- tentar DeFi complexo em privacy chain pequena sem liquidez.

Além do risco técnico, privacy coins têm pressão regulatória forte e várias foram removidas de exchanges centralizadas em diferentes jurisdições. O caminho mais seguro comercialmente é **privacidade seletiva/compliance-friendly**, não anonimato irrestrito.

---

# Veredito

**Monero não é a melhor base para smart contracts.** Ele é excelente como dinheiro privado, mas ruim como plataforma programável.

Para smart contracts privados hoje, eu olharia principalmente para:

1. **Oasis Sapphire** — melhor para Solidity/EVM;
2. **Aztec** — mais ambicioso no Ethereum, mas ainda experimental;
3. **Aleo** — L1 ZK relevante para private apps;
4. **Secret Network** — privacy contracts via Cosmos/CosmWasm;
5. **Railgun** — privacidade em DeFi EVM;
6. **Namada/Penumbra** — shielded assets/private trading;
7. **Dero** — privacy coin com smart contracts, mas nichada.

Para ganhar dinheiro solo, minha aposta seria: **private escrow/sealed-bid marketplace em Oasis Sapphire** ou **gateway de pagamento/assinatura em Monero com conciliação off-chain**.

---

### 👤 USUÁRIO *(02:54:18 UTC)*:

Quais tipos de reports de auditoria essa ferramenta aqui faz? Cheque o website e o report
https://solidityscan.com/

---

### 🤖 ASSISTENTE (ChatGPT) *(02:54:40 UTC)*:

Sim. Pelo website e pelo PDF, a SolidityScan faz principalmente **reports automatizados de segurança para smart contracts Solidity/EVM**, com algumas camadas de publicação/validação.

A leitura mais importante: **não é, por padrão, uma auditoria manual completa**. É uma ferramenta cloud de scan estático que detecta vulnerabilidades e anti-patterns, gera score de segurança e permite publicar um relatório. A própria documentação diz que ela escaneia o código do contrato, aponta vulnerabilidades conhecidas e gera um audit report com os trechos que podem levar a riscos de segurança. citeturn720096view0

## Tipos de report que aparecem no website

No menu do site, em **Audit Reports**, aparecem quatro categorias:

1. **Self Published Report**
2. **Verified Report**
3. **KYC**
4. **Manual Audit**

Isso aparece diretamente na navegação do website. citeturn778612view1

Pela documentação, quando você gera/publica um report, eles descrevem dois tipos principais de publicação:

**Self-Published Report**: o próprio usuário publica e assume a responsabilidade por revisar/identificar falsos positivos.

**Verified Report**: o report passa por verificação do time de segurança deles.

Além disso, na hora de publicar, aparece uma terceira opção: **Publish the Report after an Assisted Audit**, em que o time deles audita os achados e ajuda na publicação. citeturn385370view0

Então eu resumiria assim:

| Tipo | O que parece ser |
|---|---|
| **QuickScan Report** | Scan rápido de contrato já deployado/verificado em explorer |
| **Project/Repository Scan Report** | Scan de repositório GitHub/GitLab/Bitbucket |
| **Uploaded File/Project Report** | Scan de arquivos `.sol` enviados manualmente |
| **Self-Published Report** | Report gerado pelo scanner e publicado pelo próprio usuário |
| **Verified Report** | Report automatizado revisado/verificado pelo time da SolidityScan |
| **Assisted Audit / Manual Audit** | Camada com participação humana do time de segurança |
| **KYC Report** | Categoria separada no site, aparentemente voltada à verificação de projeto/time, não ao código em si |

## O que o report PDF contém

O PDF que você mandou é um **Security Assessment Report** para o projeto **Centel**, publicado em 26 de junho de 2026. Ele é explicitamente marcado como **Self-published**, preparado pela SolidityScan como cloud-based Smart Contract Scanner. A metodologia indicada é **Static Scanning**, ou seja, análise estática automatizada do contrato. fileciteturn0file0

A estrutura do report inclui:

- classificação de severidade;
- executive summary;
- threat summary;
- findings summary;
- detalhes das vulnerabilidades;
- histórico de scans;
- disclaimer.

No caso específico desse report, ele mostra:

| Métrica | Valor |
|---|---:|
| Security Score | **92.27/100** |
| Classificação | **Great** |
| Threat Score | **64/100** |
| Threat Risk | **Moderate Risk** |
| Linhas de código | **130** |
| Duração do scan | **5 segundos** |
| Vulnerabilidades totais | **36** |
| Critical | **0** |
| High | **0** |
| Medium | **0** |
| Low | **7** |
| Informational | **21** |
| Gas | **8** |

Os achados desse PDF são bem típicos de scanner automático:

- **Missing Events**
- **Missing Zero Address Validation**
- **Outdated Compiler Version**
- problemas de documentação **NatSpec**
- constructor poderia ser `payable`
- otimizações de gas
- constantes públicas que poderiam ser privadas
- caching de storage em memory
- imports não usados

Ou seja: nesse exemplo, ele não encontrou bug crítico; encontrou principalmente problemas de higiene, documentação, baixo risco e gas optimization. fileciteturn0file0

## O report também faz análise “token/rug-pull style”

Além da parte de vulnerabilidades de código, esse PDF tem uma seção grande de **Threat Summary**, que parece mais voltada para contratos de token. Ela avalia coisas como:

- se o source code está verificado;
- se o contrato pode mintar tokens;
- se pode queimar tokens;
- se é proxy upgradeável;
- se o owner pode blacklistar usuários;
- se é ERC-20;
- se é pausable;
- se tem funções administrativas críticas;
- se pode dar `selfdestruct`;
- se tem risco de approve race condition;
- se o owner foi encontrado;
- concentração de supply em carteiras;
- funções onlyOwner;
- whitelist;
- fees configuráveis;
- hardcoded addresses;
- hidden owner;
- special access;
- counterfeit token;
- external call risk;
- honeypot;
- antiwhale;
- buy/sell fee;
- simulação de compra, venda e transferência.

Isso é interessante porque a ferramenta não está só olhando “bug Solidity clássico”; ela também gera um tipo de **relatório de risco econômico/centralização/token safety**. No QuickScan, a documentação também diz que o resultado inclui um **Threat Scan Summary** para identificar potenciais rug pulls por análise do código do contrato. citeturn385370view1

## Entrada dos scans

A ferramenta aceita alguns fluxos:

**Contrato deployado/verificado em explorer**  
A documentação cita QuickScan para contrato deployado com código publicado em explorers, incluindo Ethereum, BSC, Polygon, Fantom, Avalanche, Cronos, Arbitrum, Celo, Optimism, XDC, Blockscout e outros. citeturn385370view1

**Repositório Git**  
Ela escaneia projetos em GitHub/GitLab/Bitbucket, permite escolher branch, arquivos e pastas, e pode configurar webhooks para disparar scans automaticamente em novos commits. citeturn385370view2

**Upload de arquivos Solidity**  
A documentação também lista upload e scan de arquivos Solidity `.sol` como feature suportada. citeturn720096view0

## Categorias de severidade usadas

O report classifica achados em:

- **Critical**
- **High**
- **Medium**
- **Low**
- **Informational**
- **Gas**

E também acompanha status dos bugs:

- **Fixed**
- **Pending Fix**
- **Won’t Fix**
- **False Positive**

No PDF que você mandou, todos os 36 achados estavam como **Pending Fix**. fileciteturn0file0

## O que essa ferramenta não substitui

O próprio report traz um disclaimer importante: ele não garante que todos os problemas serão encontrados e recomenda várias auditorias independentes, incluindo auditoria manual e bug bounty público. fileciteturn0file0

Isso bate com o posicionamento do próprio blog deles: **code review** é uma análise meticulosa feita por profissionais, enquanto **automated audit** é um scan por ferramenta para identificar potenciais vulnerabilidades. citeturn778612view4

Minha leitura: SolidityScan é muito bom como **pré-auditoria automatizada, CI security gate, segunda opinião, report comercial rápido e triagem de riscos de token**, mas não deveria ser vendido como substituto total de auditoria manual em protocolo com dinheiro real.

## Para sua ideia de projeto solo

Daria para competir ou criar algo complementar se você focar em um report mais “developer/auditor-grade”, por exemplo:

**ForgeGuard / Solidity Pre-Audit Report**

Combinando:

- Slither;
- Foundry tests;
- invariant/fuzz testing;
- análise de permissões;
- análise de upgradeability;
- threat model;
- checklist OWASP Smart Contract Top 10;
- resumo executivo;
- severity matrix;
- sugestões de testes;
- GitHub Action;
- PDF/Markdown pronto para enviar para cliente.

A oportunidade está em ir além do “scanner encontrou X”: entregar um report que diga **o que realmente importa, o que é falso positivo, qual impacto de negócio, como reproduzir, como corrigir e como provar que corrigiu**.

---

### 👤 USUÁRIO *(02:57:28 UTC)*:

aproveita e incrementa a análise acima com esse report aqui
https://solidityscan.com/published-report/block/911516917bf1d474

---

### 🤖 ASSISTENTE (ChatGPT) *(02:58:45 UTC)*:

Consegui verificar o **tipo de página**, mas não consegui extrair o conteúdo detalhado desse report específico porque a URL pública renderiza via JavaScript e, no fetch textual, só retorna “You need to enable JavaScript to run this app.” citeturn886218view0 Então não vou inventar score, quantidade de findings ou nomes de vulnerabilidades desse segundo report. Para eu analisar o conteúdo dele de verdade, o ideal é você baixar o PDF pelo botão do site e anexar aqui.

Mesmo assim, dá para incrementar a análise anterior com uma conclusão importante: esse segundo link reforça que a SolidityScan trabalha com **reports públicos hospedados**, não só PDF estático. O fluxo oficial permite gerar um report depois do scan, revisar/customizar os achados e publicar uma URL pública; a documentação diz que, depois de aprovado/publicado, o report pode ser visualizado, compartilhado por URL pública e baixado como PDF. citeturn529801search0

## O que esse segundo report adiciona à leitura da ferramenta

A análise anterior ficou muito baseada no PDF que você mandou, que era um **Security Assessment Report self-published**, com metodologia de **Static Scanning**, security score, threat summary, findings summary, vulnerabilidades por severidade e detalhes item a item. Esse PDF mostrava 36 achados no total, separados em 7 Low, 21 Informational e 8 Gas, todos como Pending Fix; também trazia score 92.27/100, scan de 5 segundos e 130 linhas analisadas. fileciteturn0file0

Com esse link público, eu adicionaria uma camada de produto:

A SolidityScan não é só um scanner que cospe PDF. Ela tenta funcionar como um **pipeline de reputação pública de smart contracts**:

1. o contrato ou repo é escaneado;
2. a ferramenta gera achados automatizados;
3. o usuário marca status como Pending Fix, Fixed, Won’t Fix ou False Positive;
4. o report pode ser publicado;
5. dependendo do tipo, pode ser self-published ou verified;
6. o link público vira um artefato para investidores, comunidade, parceiros ou clientes.

A documentação oficial confirma esse fluxo: self-published é quando o próprio usuário assume a responsabilidade por identificar/documentar falsos positivos; verified report é quando o report passa por verificação do time de segurança; e existe também a opção de publicar depois de uma assisted audit, com auditoria dos findings pelo time deles. citeturn811411search0

## Diferença prática entre os reports

Agora eu classificaria os reports da SolidityScan assim:

| Tipo | Uso principal | Confiabilidade |
|---|---|---|
| **QuickScan summary** | triagem rápida de contrato deployado | baixa/média |
| **QuickScan full report** | relatório mais completo de um contrato específico | média |
| **Self-published report** | usuário publica o scan automatizado | média-baixa se não houver revisão humana |
| **Verified report** | scan automatizado verificado pelo time da SolidityScan | média/alta |
| **Assisted audit report** | findings revisados com apoio humano | mais próximo de auditoria real |
| **Manual audit** | serviço separado, mais parecido com auditoria tradicional | maior valor, mas depende do escopo |
| **KYC report** | validação de identidade/projeto/time | não é auditoria de código |

O ponto comercial importante: a SolidityScan parece monetizar e diferenciar valor não só pelo scanner, mas pelo **grau de validação do report**. Isso é bem relevante se você estiver pensando em criar uma ferramenta concorrente ou complementar.

## O que esse padrão de report ensina para um projeto solo

Se você quisesse criar uma ferramenta tipo “ForgeGuard”, eu copiaria a estrutura geral, mas melhoraria onde a SolidityScan parece mais fraca.

A SolidityScan entrega bem:

- score visual;
- severidade por categoria;
- relatório público;
- status dos findings;
- threat summary para tokens;
- análise de rug-pull/honeypot/owner;
- relatório rápido para compartilhar;
- integração com fluxo de scan.

Mas existe espaço para um produto solo mais “auditor-grade” em cima de Foundry/Slither:

1. **validação de falsos positivos com IA + regras determinísticas**  
   A SolidityScan permite marcar falso positivo, mas o diferencial seria justificar tecnicamente por que é falso positivo.

2. **proof of fix**  
   Não apenas “Fixed”, mas mostrar commit, diff, teste novo e evidência de execução.

3. **reproduction steps**  
   Para cada finding relevante: cenário, pré-condições, PoC, impacto e correção.

4. **Foundry-native report**  
   Integrar fuzzing, invariant tests, coverage, gas snapshots e traces.

5. **threat model por tipo de contrato**  
   ERC-20, vault ERC-4626, bridge, staking, NFT, marketplace, DAO, proxy upgradeável etc.

6. **report executivo + técnico separados**  
   Um PDF para investidor/cliente e outro para dev/auditor.

7. **risk acceptance formal**  
   “Won’t Fix” com justificativa, prazo, owner e impacto residual.

8. **CI gate**  
   Falhar PR se novo finding crítico aparecer.

## Minha conclusão atualizada

Com o PDF anterior e esse segundo link, eu vejo a SolidityScan como uma mistura de:

**scanner automatizado + score de segurança + threat scan de token + gerador de report público + camada opcional de verificação humana.**

Ela é boa para **triagem, comunicação pública e pré-auditoria**, mas ainda deixa espaço para uma ferramenta solo mais técnica focada em:

> “pré-auditoria reproduzível para times Solidity, com PoCs, testes Foundry, diff de correção e relatório que um auditor humano realmente usaria.”

O que eu não faria é tentar competir com ela fazendo “mais um scanner genérico”. Eu faria algo mais especializado:

**ForgeGuard: Foundry Security Report Generator**  
Entrada: repo Solidity.  
Saída: Markdown/PDF com Slither + Foundry fuzz/invariants + threat model + PoCs + checklist OWASP + proof of fix.

Isso ataca uma dor que a SolidityScan toca só parcialmente: transformar achado automatizado em **evidência técnica confiável**.

---

### 👤 USUÁRIO *(02:59:23 UTC)*:

aqui o pdf do report que vc não abriu

---

### 🤖 ASSISTENTE (ChatGPT) *(02:59:29 UTC)*:

Agora sim — esse segundo PDF muda bastante a leitura da SolidityScan.

O primeiro report que você mandou era bem “scanner básico”: poucos achados, quase tudo low/info/gas. Já esse report do **TokenKickstarter** mostra uma camada bem mais interessante da ferramenta: ela não detecta só padrões genéricos de Solidity, mas também tenta identificar **riscos econômicos, riscos de tokenomics, riscos de AMM/Uniswap, MEV, honeypot, liquidez e bugs de lógica de negócio**.

## O que esse report é

Este PDF é um **Verified Report**, não self-published. A capa informa que o relatório automatizado foi verificado pelo time da SolidityScan. O projeto analisado é **TokenKickstarter**, publicado em **24 de abril de 2026**, com contrato na **Ethereum Mainnet**, linguagem **Solidity** e metodologia **Static Scanning**. fileciteturn1file0

Resumo dos números:

| Métrica | TokenKickstarter |
|---|---:|
| Tipo | **Verified Report** |
| Chain | Ethereum Mainnet |
| Score | **70.95/100** |
| Classificação | **Average** |
| Threat Score | **34.1/100** |
| Threat Risk | **High Risk** |
| Linhas de código | **1015** |
| Duração do scan | **110 segundos** |
| Total de vulnerabilidades | **625** |
| Critical | 0 |
| High | 2 |
| Medium | 10 |
| Low | 30 |
| Informational | 369 |
| Gas | 214 |

O report também mostra **0 fixed**, **0 false positive**, **0 won’t fix** e **655 pending fix** — aqui existe uma pequena inconsistência interna, porque o sumário fala em **625 vulnerabilities found**, mas a seção de action taken fala em **655 pending fix**. Isso já é um sinal de que, mesmo em Verified Report, o artefato precisa ser revisado criticamente. fileciteturn1file0

## Comparação com o primeiro report

| Aspecto | Centel | TokenKickstarter |
|---|---:|---:|
| Tipo | Self-published | Verified |
| Score | 92.27 / Great | 70.95 / Average |
| Threat Risk | Moderate Risk | High Risk |
| Linhas | 130 | 1015 |
| Scan | 5s | 110s |
| Total findings | 36 | 625 |
| High | 0 | 2 |
| Medium | 0 | 10 |
| Low | 7 | 30 |
| Info | 21 | 369 |
| Gas | 8 | 214 |

A diferença é grande: o primeiro parecia mais um “health check” de contrato simples. O segundo parece um report mais próximo de uma **pré-auditoria de token DeFi**, com riscos reais de AMM, reflection token, cooldown, slippage e honeypot.

## Achados de alto risco

O report traz dois achados **High**, ambos detectados como **SolidityScan AI**.

### 1. Global trade cooldown pode bloquear todo trading AMM

O primeiro High diz que a lógica de cooldown atualiza e aplica cooldown para `from` e `to` quando um dos lados é um par AMM. Como o próprio endereço do par Uniswap entra no cooldown, depois de uma trade, `_lastTradeTime[uniswapV2Pair]` é atualizado. Como todas as compras e vendas usam o mesmo par, qualquer usuário poderia bloquear as próximas trades AMM durante a janela de cooldown. fileciteturn1file0

Isso é bem mais sofisticado do que “missing zero address validation”. É uma falha de **lógica econômica / disponibilidade de mercado**.

Impacto prático:

- DoS temporário no par;
- travamento de compras/vendas;
- manipulação de liquidez;
- péssima UX para traders;
- possível uso malicioso para bloquear mercado em momentos estratégicos.

### 2. Mint recalcula reflection supply e quebra accounting

O segundo High diz que a função `mint` recalcula `_rTotal` após aumentar `_tTotal`, alterando globalmente a reflection rate sem ajustar proporcionalmente os `_rOwned` existentes. Isso pode inflar ou deflacionar saldos de holders de forma imprevisível. O report também diz que, se mintar para endereço excluído, `_tOwned` não é atualizado, causando inconsistência e possível perda de tokens. fileciteturn1file0

Esse é outro achado relevante: não é só sintaxe. É um bug em **reflection accounting**, típico de tokens estilo RFI/SafeMoon.

## Achados médios importantes

Os Mediums também são úteis para entender que tipo de report a ferramenta produz.

### Early-sell penalty bypass

O report diz que a penalidade de venda antecipada só é aplicada se `_tokenAcquisitionTime[from]` estiver definido, mas o timestamp só é registrado em compras vindas do par AMM. Se o usuário transferir os tokens para outro endereço, o novo endereço não tem timestamp e consegue vender imediatamente sem penalidade. fileciteturn1file0

Esse é um bug clássico de **state tracking incompleto**.

### Approve front-running

O report marca a vulnerabilidade conhecida do ERC-20 `approve`, em que trocar uma allowance diretamente pode permitir que o spender use tanto a allowance antiga quanto a nova se conseguir front-run. Foram **6 instâncias**. fileciteturn1file0

### Slippage e MEV em Uniswap

Há três achados relacionados:

- hardcoded slippage;
- deadline do Uniswap setado como `block.timestamp`;
- `swapAndLiquify` usando `amountOutMin = 0`, `amountTokenMin = 0` e `amountETHMin = 0`.

Na prática, isso abre espaço para **sandwich attack**, execução em preço ruim e manipulação durante operações automáticas de liquidez. fileciteturn1file0

Essa parte é bem relevante: a SolidityScan está tentando avaliar riscos de integração com DEX/AMM, não só vulnerabilidades internas do contrato.

## Threat Summary: análise de token/rug/honeypot

Esse report reforça que a SolidityScan tem uma camada de **token safety / rug-pull analysis**.

O Threat Summary aponta:

- source code verificado;
- contrato não é proxy upgradeável;
- ownership renounced;
- contrato é ERC-20;
- contrato é pausable;
- não há selfdestruct pelo owner;
- contrato vulnerável a approve race condition;
- endereços com mais de 20% do supply circulante;
- hardcoded addresses encontrados;
- liquidez não queimada;
- token classificado como honeypot;
- ausência de hidden owner;
- ausência de external call risk em funções críticas. fileciteturn1file0

Essa é uma parte que eu separaria como um tipo próprio de report:

> **Token Risk Report / Rug-Pull & Trading Behavior Report**

Ele não está só respondendo “o código compila e tem bugs?”. Ele tenta responder:

> “Esse token tem sinais de risco para comprador/trader?”

## Categorias de report que a SolidityScan parece fazer

Com os dois PDFs, eu atualizaria a classificação assim:

| Tipo de report | O que entrega |
|---|---|
| **Static Security Report** | Achados clássicos de Solidity: reentrancy, access control, compiler, zero address, eventos etc. |
| **Gas Optimization Report** | Sugestões de redução de gas, storage caching, constants privadas, loop optimization etc. |
| **Code Quality / NatSpec Report** | Documentação, visibilidade, nomes, organização de interfaces, comentários NatSpec. |
| **Token Risk Report** | Mint, burn, blacklist, whitelist, ownership, pausable, fees, supply concentration. |
| **DEX/AMM Risk Report** | Slippage, Uniswap deadline, swap-and-liquify, cooldown, sandwich/MEV. |
| **Honeypot / Rug-Pull Report** | Buy/sell simulation, honeypot behavior, liquidity burn/lock, owner powers. |
| **Verified Report** | Report automatizado revisado/verificado pelo time SolidityScan. |
| **Self-Published Report** | Report gerado e publicado pelo próprio usuário. |
| **AI-Assisted Findings** | Achados mais contextuais, como cooldown causando DoS e reflection accounting quebrado. |

## O ponto mais interessante: “SolidityScan AI”

No primeiro report, praticamente tudo parecia regra automatizada comum. Neste segundo, os achados mais relevantes aparecem com detection method **SolidityScan AI**:

- global trade cooldown causando pair-level DoS;
- minting quebrando reflection accounting;
- early-sell penalty bypass;
- swap-and-liquify sem slippage protection;
- unsafe ERC20 withdrawal ignorando return value.

Isso sugere que a ferramenta tem uma camada tentando interpretar **intenção e fluxo de negócio**, além de regras estáticas fixas. Para um produto solo concorrente/complementar, esse é exatamente o ponto mais difícil e mais valioso.

## Mas o report também mostra limitações

Esse segundo PDF é melhor, mas também expõe problemas.

Primeiro: há inconsistência numérica entre **625 vulnerabilities found** e **655 pending fix**. fileciteturn1file0

Segundo: o Threat Summary diz que “the contract cannot mint new tokens”, mas um dos Highs fala explicitamente de uma função `mint` que recalcula reflection supply. Isso pode ser uma contradição, um falso positivo, uma limitação do módulo de threat summary, ou uma diferença entre “mint detectável como privilégio ativo” e “função mint no código”. Sem revisão manual, não dá para aceitar cegamente. fileciteturn1file0

Terceiro: ele mistura muitos achados realmente importantes com centenas de itens de documentação/gas/NatSpec. Isso pode gerar ruído. Em um report com 625 achados, o cliente precisa de priorização forte, senão se perde.

## O que isso ensina para sua possível ferramenta solo

Agora eu vejo uma oportunidade ainda mais clara para uma ferramenta complementar, não concorrente genérica.

A SolidityScan já faz bem:

- scan rápido;
- report visual;
- score;
- publicação pública;
- categorização de severidade;
- análise token/rug/honeypot;
- algumas detecções contextuais com IA;
- verified report.

O espaço para você seria construir algo mais **audit-engineering**, focado em prova, reprodução e correção.

Exemplo de produto:

# ForgeGuard: Pre-Audit Reports for Solidity Teams

Diferenciais contra um scanner genérico:

1. **Prioridade real, não só lista de findings**  
   Separar “risco explorável agora” de “higiene de código”.

2. **PoC Foundry para cada High/Medium**  
   Exemplo: um teste que demonstra o cooldown bloqueando o par AMM.

3. **Invariant testing**  
   Para o bug de reflection accounting, criar invariants como: soma dos saldos refletidos não deve divergir do total supply, mint não deve alterar saldos de holders existentes indevidamente, excluded accounts devem manter consistência.

4. **MEV simulation**  
   Para slippage zero e deadline ruim, simular sandwich ou execução desfavorável.

5. **Proof of Fix**  
   Após correção, rodar o mesmo teste e mostrar que falha antes e passa depois.

6. **Noise reduction**  
   Agrupar 369 infos e 214 gas em apêndice, enquanto o corpo principal foca em 2 High + 10 Medium + riscos de tokenomics.

7. **Business impact**  
   Traduzir “amountOutMin = 0” para “o protocolo pode vender tokens do contrato por preço arbitrariamente ruim durante swap automático”.

## Veredito atualizado

Com esse segundo PDF, eu diria que a SolidityScan faz quatro grandes famílias de report:

1. **Security Static Analysis Report**
2. **Token/Rug/Honeypot Threat Report**
3. **Gas & Code Quality Report**
4. **Verified/Public Audit Report**

O report do TokenKickstarter é bem mais representativo do produto completo do que o primeiro. Ele mostra que a ferramenta tenta capturar risco real de DeFi/tokenomics, como DoS em AMM, reflection accounting quebrado, bypass de penalty e MEV por slippage ruim.

Mas, mesmo sendo verified, ele ainda tem inconsistências e muito ruído. Então a oportunidade solo não é “fazer outro SolidityScan menor”. É fazer uma camada que transforme achados em:

> **evidência reproduzível + teste Foundry + correção sugerida + proof-of-fix + priorização executiva.**

---

### 👤 USUÁRIO *(03:04:33 UTC)*:

Agora, com base em todos os achados, monte um mapa de especificações para o framework spec driven development, para criarmos uma plataforma de audotira de contratos inteligentes solidity evm bem próxima da plataforma solidityscan do zero.

---

### 🤖 ASSISTENTE (ChatGPT) *(03:04:47 UTC)*:

Abaixo está um **mapa de especificações SDD — Spec Driven Development** para construirmos, do zero, uma plataforma de auditoria de smart contracts Solidity/EVM próxima da SolidityScan.

A ideia é organizar o produto não como “vamos codar um scanner”, mas como um conjunto de **specs executáveis, testáveis e evolutivas**, onde cada capacidade do sistema nasce de uma especificação clara: entrada, saída, regra, severidade, score, evidência, falso positivo, correção e validação.

---

# 1. Visão do produto

## Nome conceitual

**EVM AuditScan Platform**

## Objetivo

Criar uma plataforma SaaS/API para análise automatizada, semiassistida e publicável de contratos inteligentes Solidity/EVM, cobrindo:

- segurança de código;
- qualidade de código;
- documentação NatSpec;
- otimização de gas;
- risco de tokenomics;
- risco de owner/admin;
- risco de DEX/AMM;
- honeypot/rug-pull indicators;
- simulações de compra, venda e transferência;
- relatórios públicos self-published e verified;
- integração com repositórios, block explorers e CI/CD.

Os reports da SolidityScan que analisamos mostram dois padrões importantes: um report simples/self-published com 36 achados majoritariamente low/info/gas, e um report verified muito mais completo com 625 vulnerabilidades, 2 high, 10 medium, 30 low, 369 informational e 214 gas. Isso indica que a plataforma precisa suportar tanto **scan leve de triagem** quanto **report profundo de token/DeFi**. fileciteturn2file2 fileciteturn2file9

---

# 2. Premissas de produto extraídas dos reports

## Premissa 1 — A plataforma é primariamente de static scanning

Os dois reports declaram metodologia **Static Scanning** e descrevem o scanner como uma ferramenta cloud que analisa código Solidity, bibliotecas e práticas seguras, cobrindo vulnerabilidades de gas até vulnerabilidades capazes de gerar perda de fundos. fileciteturn2file0 fileciteturn2file2

## Premissa 2 — O report precisa ter taxonomia clara de severidade

A taxonomia observada é:

- Critical;
- High;
- Medium;
- Low;
- Informational;
- Gas.

Além disso, os achados podem ter status como **Fixed**, **Pending Fix**, **Won’t Fix** e **False Positive**. fileciteturn2file7

## Premissa 3 — A plataforma precisa separar “security score” de “threat score”

No report TokenKickstarter, o security score é **70.95/100**, mas o threat score é **34.1/100** e o risco é **High Risk**. Isso mostra que o score técnico do código e o risco econômico/comportamental do token não são a mesma coisa. fileciteturn2file0

## Premissa 4 — O produto deve cobrir mais do que bugs clássicos

O report TokenKickstarter inclui achados como:

- cooldown global bloqueando trades AMM;
- mint quebrando reflection accounting;
- bypass de early-sell penalty;
- slippage hardcoded;
- deadline Uniswap como `block.timestamp`;
- `swapAndLiquify` sem proteção de slippage;
- honeypot;
- liquidez não queimada;
- concentração de supply.

Esses achados mostram que o produto precisa cobrir **lógica de negócio DeFi/tokenomics**, não apenas padrões genéricos de Solidity. fileciteturn2file8

---

# 3. Mapa macro de especificações

## SPEC-000 — Product Charter

**Objetivo:** definir o que a plataforma é e o que ela não é.

**A plataforma deve:**

- escanear contratos Solidity/EVM;
- gerar findings estruturados;
- classificar severidade;
- gerar score;
- sugerir remediações;
- gerar relatório HTML/PDF;
- permitir publicação pública;
- permitir revisão humana;
- permitir integração CI/CD.

**A plataforma não deve prometer:**

- garantia absoluta de segurança;
- substituição total de auditoria manual;
- recomendação de investimento;
- validação jurídica/regulatória;
- garantia de que o token é seguro para comprar.

Essa restrição é importante porque os próprios reports deixam claro que auditoria automatizada não garante encontrar todos os problemas e recomendam auditorias manuais independentes e bug bounty. fileciteturn2file1

---

# 4. Domínio principal da plataforma

## SPEC-001 — Domain Model

### Entidades centrais

```text
Organization
 └── Project
      ├── ScanTarget
      │    ├── ContractAddress
      │    ├── Repository
      │    └── UploadedFiles
      ├── ScanRun
      │    ├── CompilationUnit
      │    ├── DetectorExecution
      │    ├── Finding
      │    ├── Score
      │    └── Report
      └── Publication
           ├── SelfPublished
           ├── Verified
           └── AssistedAudit
```

### Entidades técnicas

```text
Contract
 ├── SourceFile
 ├── AST
 ├── Bytecode
 ├── ABI
 ├── InheritanceGraph
 ├── ControlFlowGraph
 ├── CallGraph
 ├── StorageLayout
 ├── Modifiers
 ├── Events
 ├── ExternalCalls
 ├── TokenMetadata
 ├── DEXIntegrations
 └── OwnershipModel
```

### Entidade Finding

Todo achado deve seguir um schema único:

```json
{
  "finding_id": "AMM-COOLDOWN-DOS-001",
  "title": "Global trade cooldown can block all AMM trading",
  "severity": "High",
  "category": "DEX_AMM",
  "detection_method": "StaticRule | SemanticRule | Simulation | AIReview | ManualReview",
  "confidence": "High",
  "instances": 1,
  "status": "Pending Fix",
  "file": "contract.sol",
  "line_start": 1000,
  "line_end": 1030,
  "description": "...",
  "impact": "...",
  "exploit_scenario": "...",
  "recommendation": "...",
  "references": [],
  "evidence": {
    "code_snippet": "...",
    "trace": null,
    "simulation": null
  },
  "false_positive_notes": null
}
```

---

# 5. Tipos de scan

## SPEC-010 — QuickScan por endereço

**Entrada:**

- chain;
- contract address.

**Fluxo:**

1. buscar código verificado no explorer;
2. identificar ABI, source, compiler, proxy, metadata;
3. compilar localmente se possível;
4. rodar static detectors;
5. rodar token threat detectors;
6. gerar score rápido;
7. gerar resumo visual.

**Critérios de aceite:**

- deve falhar com mensagem clara se o código não estiver verificado;
- deve detectar chain e explorer;
- deve gerar report em menos de X minutos para contratos até Y linhas;
- deve marcar scan como “source verified” ou “source unavailable”.

---

## SPEC-011 — Repository Scan

**Entrada:**

- GitHub/GitLab/Bitbucket repo;
- branch;
- path opcional;
- framework detectado: Foundry, Hardhat, Truffle, Brownie.

**Fluxo:**

1. clonar repositório;
2. detectar package manager;
3. detectar versão do Solidity;
4. instalar dependências em sandbox;
5. compilar;
6. gerar AST e artifacts;
7. escanear todos os contratos relevantes;
8. gerar findings por contrato e por projeto.

**Critérios de aceite:**

- deve suportar múltiplas versões de `solc`;
- deve preservar source mapping;
- deve identificar contratos abstratos, interfaces, libraries e deployables;
- deve diferenciar finding em código próprio versus dependency.

---

## SPEC-012 — Upload Scan

**Entrada:**

- arquivos `.sol`;
- zip de projeto;
- metadados opcionais.

**Critérios de aceite:**

- deve validar tamanho máximo;
- deve impedir execução insegura;
- deve permitir scan parcial mesmo sem compilação completa;
- deve indicar baixa confiança quando não houver contexto suficiente.

---

# 6. Tipos de report

## SPEC-020 — Report Types

A plataforma deve suportar quatro tipos principais.

### 1. Internal Draft Report

Report privado, usado enquanto o projeto corrige os achados.

### 2. Self-Published Report

Report público publicado pelo próprio usuário.

O primeiro PDF é um exemplo desse modelo: o report Centel aparece como **Self-published**, preparado pela SolidityScan, com score, summary, threat summary e vulnerability details. fileciteturn2file6

### 3. Verified Report

Report automatizado revisado/verificado pelo time da plataforma.

O segundo PDF é um exemplo: a capa do TokenKickstarter declara que o report automatizado foi verificado pelo time da SolidityScan. fileciteturn2file3

### 4. Assisted / Manual Audit Report

Report com revisão humana, comentários manuais e validação de falsos positivos.

---

## SPEC-021 — Estrutura obrigatória do report

Todo report deve conter:

1. Capa;
2. Tipo do report;
3. Executive Summary;
4. Security Score;
5. Threat Score;
6. Metadados do contrato/projeto;
7. Vulnerability Classification;
8. Threat Summary;
9. Findings Summary;
10. Action Taken;
11. Vulnerability Details;
12. Scan History;
13. Disclaimer.

Essa estrutura replica o padrão observado nos PDFs: ambos têm executive summary, threat summary, findings summary, vulnerability details, scan history e disclaimer. fileciteturn2file0 fileciteturn2file1

---

# 7. Sistema de severidade

## SPEC-030 — Severity Taxonomy

### Critical

Achado pode levar diretamente à perda significativa de fundos, apropriação indevida, mint arbitrário, drain, bypass crítico de autorização ou corrupção irreversível de estado.

### High

Risco significativo para o contrato ou organização, com possibilidade de perda de fundos, DoS relevante, manipulação grave, quebra de accounting ou exploração sob condições razoáveis.

### Medium

Afeta segurança, integridade ou disponibilidade, mas com impacto condicionado, mitigável ou menos direto.

### Low

Impacto limitado, falha de validação, rastreabilidade, manutenção ou edge case.

### Informational

Boas práticas, documentação, legibilidade, organização e clareza.

### Gas

Otimizações de custo sem impacto direto na segurança.

Essa taxonomia vem diretamente da estrutura dos reports analisados. fileciteturn2file7

---

# 8. Sistema de status dos achados

## SPEC-031 — Finding Lifecycle

Estados:

```text
Detected
 └── Triaged
      ├── Pending Fix
      ├── Fixed
      ├── False Positive
      ├── Won't Fix
      └── Risk Accepted
```

### Regras

- Todo finding nasce como `Detected`.
- Após revisão automática ou humana, vira `Triaged`.
- `Fixed` exige novo scan ou proof-of-fix.
- `False Positive` exige justificativa.
- `Won’t Fix` exige justificativa e impacto residual.
- `Risk Accepted` exige owner, data, justificativa e severidade residual.

Nos reports, o modelo base tem Fixed, False Positive, Won’t Fix e Pending Fix; para nossa plataforma, eu adicionaria `Risk Accepted`, que é mais profissional para B2B. fileciteturn2file7

---

# 9. Scoring engine

## SPEC-040 — Security Score

O **Security Score** deve medir qualidade/risco do código com base em:

- severidade;
- quantidade de instâncias;
- confiança;
- linhas de código;
- tipo de contrato;
- exposição externa;
- presença de testes/proofs;
- status do finding.

### Fórmula inicial sugerida

```text
base_score = 100

penalty =
  critical_count * 25 +
  high_count * 12 +
  medium_count * 5 +
  low_count * 1.5 +
  info_count * 0.15 +
  gas_count * 0.05

normalization_factor = sqrt(lines_of_code / 100)

security_score = max(0, 100 - penalty / normalization_factor)
```

Depois essa fórmula deve ser calibrada com corpus real.

---

## SPEC-041 — Threat Score

O **Threat Score** deve medir risco comportamental/econômico, especialmente para tokens.

Entradas:

- honeypot detectado;
- buy/sell simulation;
- liquidity lock/burn;
- owner privileges;
- mint/burn capabilities;
- blacklist/whitelist;
- fee mutability;
- supply concentration;
- pausable;
- proxy upgradeability;
- hidden owner;
- hardcoded addresses;
- AMM/DEX risk;
- slippage/MEV exposure.

No TokenKickstarter, o report mostra exatamente esse tipo de avaliação: source verified, ownership renounced, ERC-20, pausable, approve race condition, supply concentration, hardcoded addresses, liquidity burn status, honeypot e outros indicadores. fileciteturn2file0

---

# 10. Famílias de detectores

## SPEC-100 — Detector Registry

Cada detector deve pertencer a uma família:

```text
SEC      Core Security
ERC      ERC Standards
OWN      Ownership/Admin Risk
TOK      Tokenomics Risk
AMM      AMM/DEX/MEV Risk
HNY      Honeypot/Rug Risk
GAS      Gas Optimization
DOC      NatSpec/Documentation
QUAL     Code Quality
COMP     Compiler/Pragma
SIM      Dynamic Simulation
AI       AI-assisted Semantic Findings
```

---

# 11. Core Security Detectors

## SPEC-SEC-001 — Missing Zero Address Validation

**Motivação:** apareceu nos dois reports.

**Detecta:**

- função recebe `address`;
- endereço é usado em state change, ownership, mint, transfer, router, pair ou config crítica;
- não há `require(addr != address(0))`.

**Severidade padrão:** Low ou Medium, dependendo do uso.

**Critérios de aceite:**

```gherkin
Given a function sets an owner address
And the input address is not checked against address(0)
When the scanner analyzes the function
Then it must emit SEC-ZERO-ADDRESS-001
And classify severity at least Low
```

---

## SPEC-SEC-002 — Missing Events

**Detecta:**

- função altera estado crítico;
- não emite evento.

**Estado crítico inclui:**

- owner/admin;
- fees;
- router/pair;
- pause/unpause;
- mint/burn;
- whitelist/blacklist;
- treasury;
- limits;
- cooldown.

O Centel report encontrou Missing Events como low, e o TokenKickstarter encontrou 15 instâncias. fileciteturn2file8

---

## SPEC-SEC-003 — Unsafe ERC20 Transfer Return Value

**Detecta:**

```solidity
IERC20(token).transfer(to, amount);
```

sem verificar retorno ou sem usar `SafeERC20`.

**Severidade padrão:** Low/Medium.

No TokenKickstarter, o report encontrou `withdrawTokens` chamando `IERC20(token).transfer(msg.sender, amount)` sem checar retorno, indicando risco de falha silenciosa. fileciteturn2file8

---

## SPEC-SEC-004 — NonReentrant Modifier Placement

**Detecta:**

- função tem `nonReentrant`;
- `nonReentrant` não é o primeiro modifier.

**Critério:**

```gherkin
Given a function has modifiers [onlyOwner, nonReentrant]
When the scanner analyzes modifier order
Then it must flag nonReentrant placement risk
```

---

## SPEC-SEC-005 — ABI EncodePacked Collision

**Detecta:**

- uso de `abi.encodePacked`;
- múltiplos argumentos dinâmicos;
- resultado usado em hash, assinatura, id, permit, claim ou autorização.

**Severidade:**

- Informational se sem input externo;
- Medium se usado para autorização, assinatura ou claim.

---

# 12. ERC Standard Detectors

## SPEC-ERC-001 — ERC20 Approve Front-Running

**Detecta:**

- implementação clássica de `approve(spender, amount)`;
- allowance sobrescrita sem mitigação;
- ausência de `increaseAllowance` / `decreaseAllowance` ou enforce zero-first.

O TokenKickstarter report encontrou 6 instâncias de approve front-running como Medium. fileciteturn2file8

**Aceite:**

```gherkin
Given an ERC20 contract implements approve by directly replacing allowance
When spender has an existing non-zero allowance
Then the scanner must flag ERC20 approve front-running risk
```

---

## SPEC-ERC-002 — ERC20 Zero Transfer Compatibility

**Detecta:**

- transferências ERC-20 externas com valor potencialmente zero;
- ausência de check `if (amount > 0)`.

**Racional:** alguns tokens antigos ou não padronizados podem reverter em zero transfer.

---

# 13. Compiler and Build Detectors

## SPEC-COMP-001 — Floating Pragma

**Detecta:**

```solidity
pragma solidity ^0.8.0;
pragma solidity >=0.8.0;
```

**Severidade:** Low.

---

## SPEC-COMP-002 — Outdated Compiler Version

**Detecta:**

- versão antiga do Solidity;
- versão com bugs conhecidos;
- versão abaixo da baseline configurada.

Nos dois reports, SolidityScan marcou contratos que poderiam ser compilados com versão mais recente. fileciteturn2file2 fileciteturn2file8

---

# 14. Ownership/Admin Risk

## SPEC-OWN-001 — Owner Powers Inventory

**Objetivo:** criar inventário de poderes do owner/admin.

Deve detectar se owner pode:

- mintar;
- burnar;
- pausar;
- blacklistar;
- whitelistar;
- alterar fees;
- alterar router;
- alterar pair;
- alterar limites;
- sacar tokens;
- alterar supply;
- excluir usuários de taxas;
- atualizar endereços críticos;
- atualizar lógica/proxy.

O Threat Summary dos reports mostra exatamente esse tipo de análise: se owners podem blacklistar, setar fees, modificar balances, se existe ownership renounced, se há hidden owner, special access etc. fileciteturn2file0

---

## SPEC-OWN-002 — Hidden Owner Detection

**Detecta:**

- variáveis não chamadas `owner` com poderes equivalentes;
- roles privadas;
- hardcoded privileged addresses;
- mappings de privilégio;
- modifiers customizados;
- `tx.origin` ou `msg.sender` comparado contra endereço fixo.

---

## SPEC-OWN-003 — Hardcoded Address Risk

**Detecta:**

- endereços literais no código;
- endereços usados em router, pair, treasury, owner, marketing wallet, burn wallet, token dependency.

O TokenKickstarter report marcou hardcoded addresses como risco no threat summary e também como finding. fileciteturn2file9

---

# 15. Tokenomics Risk

## SPEC-TOK-001 — Mint Capability Detection

**Detecta:**

- funções que aumentam `_totalSupply`, `_tTotal`, `_rTotal`;
- funções `mint`, `_mint`, `issue`, `create`, `reflectionFromToken` suspeitas;
- alterações indiretas de supply.

**Observação importante:** o TokenKickstarter report mostrou uma aparente tensão entre threat summary dizendo que o contrato não pode mintar novos tokens e um High finding sobre função `mint` recalculando reflection supply. Nossa plataforma deve tratar esse tipo de divergência como uma anomalia de consistência do report. fileciteturn2file0 fileciteturn2file8

---

## SPEC-TOK-002 — Reflection Accounting Integrity

**Detecta contratos com:**

- `_rTotal`;
- `_tTotal`;
- `_rOwned`;
- `_tOwned`;
- excluded accounts;
- reflection rate;
- fees redistributivas.

**Invariantes sugeridas:**

```text
Invariant 1: mint não deve alterar saldo proporcional de holders existentes indevidamente.
Invariant 2: soma efetiva de balances não deve divergir do total supply.
Invariant 3: excluded accounts devem manter _tOwned e _rOwned consistentes.
Invariant 4: mudanças em _tTotal não devem recalcular _rTotal sem ajuste proporcional.
```

Esse detector nasce diretamente do High finding do TokenKickstarter: mint recalculando reflection supply, distorcendo balances e quebrando accounting. fileciteturn2file8

---

## SPEC-TOK-003 — Early-Sell Penalty Bypass

**Detecta:**

- penalidade baseada em timestamp por endereço;
- timestamp registrado apenas em compras;
- transferências não propagam acquisition time;
- endereço novo consegue vender sem penalidade.

O TokenKickstarter report encontrou exatamente esse bypass: transferir tokens para endereço fresco remove o acquisition timestamp e permite vender sem early-sell penalty. fileciteturn2file8

---

## SPEC-TOK-004 — Supply Concentration

**Detecta:**

- carteiras com mais de X% do supply;
- owner com mais de X%;
- top holders;
- LP;
- burn address;
- contract balance.

**Thresholds:**

```text
> 5%: monitorar
> 10%: risco moderado
> 20%: risco alto
> 50%: risco extremo
```

O TokenKickstarter report apontou endereços com mais de 20% do supply circulante. fileciteturn2file0

---

# 16. AMM/DEX/MEV Risk

## SPEC-AMM-001 — Pair-Level Cooldown DoS

**Detecta:**

- lógica de cooldown aplicada a `from` e `to`;
- uma das partes é AMM pair;
- `_lastTradeTime[pair]` é atualizado;
- trades subsequentes envolvendo o mesmo pair podem reverter.

Esse foi um High finding no TokenKickstarter: uma trade atualiza cooldown do par Uniswap e qualquer usuário pode bloquear trades AMM subsequentes durante a janela de cooldown. fileciteturn2file8

**Aceite:**

```gherkin
Given an ERC20 token applies cooldown to both from and to
And from or to can be the AMM pair
When a buy or sell occurs
Then the scanner must detect that the AMM pair itself receives cooldown state
And emit AMM-COOLDOWN-DOS-001 as High
```

**Remediação sugerida:**

- não aplicar cooldown ao pair;
- aplicar cooldown apenas ao usuário final;
- separar buy cooldown e sell cooldown;
- ignorar `from == pair` e `to == pair` para state tracking de cooldown do pair.

---

## SPEC-AMM-002 — Hardcoded Slippage

**Detecta:**

- slippage fixa;
- `amountOutMin` calculado com percentual constante;
- ausência de parâmetro configurável;
- slippage sem oracle/quote.

O TokenKickstarter report marcou hardcoded slippage for Uniswap como Medium. fileciteturn2file8

---

## SPEC-AMM-003 — Deadline Set to Block Timestamp

**Detecta:**

```solidity
deadline = block.timestamp
```

em swaps Uniswap.

**Risco:** remove proteção real de deadline e permite execução em condições desfavoráveis.

O report TokenKickstarter marcou esse caso como Medium. fileciteturn2file8

---

## SPEC-AMM-004 — Zero Slippage in SwapAndLiquify

**Detecta:**

```solidity
amountOutMin = 0
amountTokenMin = 0
amountETHMin = 0
```

em:

- `swapExactTokensForETHSupportingFeeOnTransferTokens`;
- `addLiquidityETH`;
- funções de auto-liquidity.

O report TokenKickstarter classificou isso como Medium e explicou risco de MEV sandwich e manipulação de preço. fileciteturn2file8

---

# 17. Honeypot / Rug-Pull Detectors

## SPEC-HNY-001 — Buy Simulation

**Entrada:**

- chain;
- token;
- router;
- pair;
- amount in.

**Saída:**

- success/fail;
- buy tax;
- gas used;
- revert reason;
- balance received.

---

## SPEC-HNY-002 — Sell Simulation

**Entrada:**

- token balance simulado;
- router/pair.

**Saída:**

- success/fail;
- sell tax;
- gas used;
- revert reason;
- amount out.

No report TokenKickstarter, a plataforma conclui que o contrato é honeypot, o que exige exatamente esse tipo de simulação de comportamento de compra/venda. fileciteturn2file0

---

## SPEC-HNY-003 — Liquidity Lock/Burn Status

**Detecta:**

- LP tokens queimados;
- LP tokens em locker;
- LP tokens em carteira acessível;
- unlock date;
- percentual da liquidez protegida.

O TokenKickstarter report mostra Liquidity Burn Status como **Not Burnt**. fileciteturn2file0

---

# 18. Gas Optimization Detectors

## SPEC-GAS-001 — Storage Variable Caching

Detecta múltiplos `SLOADs` da mesma variável em uma função e recomenda caching em variável local.

O Centel report tem esse finding explicitamente, explicando que `SLOADs` são mais caros do que `MLOAD/MSTORE`. fileciteturn2file4

---

## SPEC-GAS-002 — Unused Imports

Detecta imports não utilizados.

O Centel report marcou unused imports como gas issue. fileciteturn2file4

---

## SPEC-GAS-003 — Public Constants Can Be Private

Detecta constantes públicas que geram getters desnecessários.

---

## SPEC-GAS-004 — Array Length Caching

Detecta loops que acessam `array.length` repetidamente.

---

## SPEC-GAS-005 — Bitmaps Instead of Booleans

Detecta múltiplos booleans que poderiam ser empacotados em bitmap.

O TokenKickstarter report tem esse achado como gas optimization, explicando que booleans separados desperdiçam storage slots. fileciteturn2file5

---

# 19. Documentation / NatSpec Detectors

## SPEC-DOC-001 — Missing NatSpec Author

Detecta ausência de `@author`.

## SPEC-DOC-002 — Missing NatSpec Dev

Detecta ausência de `@dev`.

## SPEC-DOC-003 — Missing NatSpec Notice

Detecta ausência de `@notice`.

## SPEC-DOC-004 — Missing Inheritdoc

Detecta override sem `@inheritdoc`.

## SPEC-DOC-005 — Missing Indexed Event Parameters

Detecta eventos sem `indexed` em campos relevantes.

Esses detectores são importantes para completar score e maturidade, mas devem ficar em seção separada do report para não poluir os achados críticos. O TokenKickstarter tem centenas de findings informacionais, incluindo NatSpec, comentários, naming e documentação. fileciteturn2file9

---

# 20. AI-assisted semantic analysis

## SPEC-AI-001 — Semantic Finding Generator

**Objetivo:** detectar bugs de lógica de negócio que regras simples não capturam bem.

Entradas:

- AST;
- call graph;
- state variables;
- modifiers;
- eventos;
- nomes de funções;
- comentários;
- padrões de tokenomics;
- integração com AMM;
- resultados de detectores estáticos.

Saídas:

- finding candidato;
- severidade sugerida;
- confiança;
- explicação;
- trecho de código;
- teste Foundry sugerido;
- remediação.

No TokenKickstarter, os achados mais interessantes aparecem como **SolidityScan AI**, incluindo cooldown DoS, reflection accounting, early-sell penalty bypass e slippage zero em swap-and-liquify. fileciteturn2file8

---

## SPEC-AI-002 — AI Finding Validation

A IA não deve publicar finding direto sem validação.

Pipeline:

```text
AI Candidate
  → Rule Cross-Check
  → Static Evidence Required
  → Optional Simulation
  → Confidence Score
  → Human Review if Verified Report
```

Critérios mínimos:

- finding precisa apontar arquivo/linha;
- precisa ter explicação reproduzível;
- precisa ter condição de impacto;
- precisa ter sugestão de remediação;
- precisa indicar incerteza.

---

# 21. Proof-of-Fix e testes Foundry

Aqui está o diferencial que eu colocaria na nossa plataforma.

## SPEC-POF-001 — Reproducible Finding

Para cada High e Medium, a plataforma deve tentar gerar:

- PoC Foundry;
- invariant test;
- fuzz test;
- cenário de reprodução;
- trace de execução.

Exemplo para cooldown DoS:

```solidity
function testPairCooldownBlocksAllTrading() public {
    buy(userA);
    vm.expectRevert();
    buy(userB);
}
```

Exemplo para reflection accounting:

```solidity
function invariantMintDoesNotDistortExistingBalances() public {
    uint256 beforeBalance = token.balanceOf(holder);
    token.mint(newHolder, amount);
    uint256 afterBalance = token.balanceOf(holder);

    assertApproxEqRel(afterBalance, beforeBalance, tolerance);
}
```

---

## SPEC-POF-002 — Proof-of-Fix

Um finding só pode ser marcado como `Fixed` se:

- o código foi alterado;
- o scan foi reexecutado;
- o detector não acusa mais;
- o teste de reprodução passa;
- ou houve justificativa manual.

---

# 22. Report UX

## SPEC-UX-001 — Executive View

Deve mostrar:

- score;
- risco geral;
- quantidade por severidade;
- principais riscos;
- status dos achados;
- se o report é self-published, verified ou manual;
- disclaimer.

---

## SPEC-UX-002 — Technical View

Deve mostrar para cada finding:

- título;
- severidade;
- confiança;
- categoria;
- arquivo/linha;
- trecho de código;
- impacto;
- cenário de exploração;
- recomendação;
- status;
- diff de correção, se houver;
- teste gerado, se houver.

---

## SPEC-UX-003 — Noise Management

Para reports com centenas de achados:

- High e Medium no corpo principal;
- Low em seção secundária;
- Informational e Gas em apêndice;
- agrupamento por tipo;
- filtros por severidade/status/categoria;
- “top 10 risks” automático.

Isso resolve um problema observado no TokenKickstarter: há achados importantes, mas também 369 informacionais e 214 de gas, o que pode gerar ruído. fileciteturn2file9

---

# 23. API pública

## SPEC-API-001 — Scan API

```http
POST /api/v1/scans
```

```json
{
  "target_type": "contract_address",
  "chain_id": 1,
  "address": "0x...",
  "scan_profile": "quick | full | token-risk | ci"
}
```

---

## SPEC-API-002 — Findings API

```http
GET /api/v1/scans/{scan_id}/findings
```

Filtros:

```text
severity
category
status
detector_id
contract
file
confidence
```

---

## SPEC-API-003 — Report API

```http
POST /api/v1/reports
GET /api/v1/reports/{report_id}
POST /api/v1/reports/{report_id}/publish
```

---

# 24. CI/CD e DevSecOps

## SPEC-CI-001 — GitHub Action

Exemplo:

```yaml
name: EVM AuditScan

on:
  pull_request:
    paths:
      - "contracts/**/*.sol"

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: evm-auditscan/action@v1
        with:
          fail-on: "high"
          report-format: "sarif,json,markdown"
```

## SPEC-CI-002 — Quality Gates

Configuração:

```yaml
fail_on:
  critical: true
  high: true
  medium_new: true

allow_existing_findings: true
baseline_file: ".auditscan-baseline.json"
```

---

# 25. Verificação humana

## SPEC-VER-001 — Verified Report Workflow

Fluxo:

```text
User requests verified report
 → Platform locks scan version
 → Human reviewer validates High/Medium
 → Reviewer marks false positives
 → Reviewer adds notes
 → Report receives verified seal
 → Public URL is generated
```

Critérios:

- High e Medium não podem ir para verified sem revisão;
- contradições internas devem ser resolvidas;
- contagens devem bater;
- findings AI precisam de evidência.

Isso é especialmente importante porque o TokenKickstarter report mostra uma inconsistência entre total vulnerabilities e pending fix, além da tensão entre “cannot mint” no threat summary e finding de mint/reflection. fileciteturn2file0 fileciteturn2file9

---

# 26. KYC / Project Trust opcional

## SPEC-KYC-001 — Project Identity Report

Não é auditoria de código.

Campos:

- nome da organização;
- website;
- contato;
- redes sociais;
- verificação de domínio;
- verificação de identidade;
- status público.

Esse módulo deve ficar separado para não confundir “time verificado” com “contrato seguro”.

---

# 27. Banco de dados mínimo

## SPEC-DB-001 — Tabelas principais

```text
organizations
projects
scan_targets
scan_runs
contracts
source_files
detectors
findings
finding_instances
finding_status_history
scores
reports
report_publications
review_notes
proof_of_fix_tests
```

## SPEC-DB-002 — Detector Registry

```sql
detectors (
  id,
  code,
  name,
  family,
  default_severity,
  description,
  remediation_template,
  enabled,
  version
)
```

## SPEC-DB-003 — Findings

```sql
findings (
  id,
  scan_run_id,
  detector_id,
  severity,
  confidence,
  status,
  title,
  description,
  impact,
  remediation,
  detection_method,
  instances_count
)
```

---

# 28. Arquitetura técnica

## SPEC-ARCH-001 — Componentes

```text
Frontend Web App
 ├── Dashboard
 ├── Report Viewer
 ├── Findings Triage
 └── Project Settings

API Gateway
 ├── Auth
 ├── Project API
 ├── Scan API
 ├── Report API
 └── Billing API

Scan Orchestrator
 ├── Queue
 ├── Worker Pool
 ├── Sandbox Manager
 └── Artifact Store

Source Ingestion
 ├── Explorer Fetcher
 ├── Git Fetcher
 └── Upload Handler

Solidity Analysis Engine
 ├── Compiler Manager
 ├── AST Parser
 ├── CFG/CallGraph Builder
 ├── Static Rule Engine
 ├── Semantic Analyzer
 ├── Token Risk Analyzer
 ├── AMM/DEX Analyzer
 ├── Simulation Engine
 └── AI Review Layer

Report Engine
 ├── Score Calculator
 ├── PDF Generator
 ├── HTML Report
 ├── Public Report Publisher
 └── Verification Seal Manager
```

---

# 29. Roadmap por fases

## Fase 1 — MVP scanner

Entrega:

- upload `.sol`;
- scan por endereço;
- parser AST;
- 30 detectores básicos;
- findings com severidade;
- score simples;
- report HTML;
- export Markdown/PDF.

Detectores MVP:

- zero address;
- missing events;
- floating pragma;
- outdated compiler;
- hardcoded addresses;
- unsafe ERC20 return;
- approve front-running;
- missing NatSpec;
- storage caching;
- unused imports.

---

## Fase 2 — Token Risk Scanner

Entrega:

- ERC-20 detector;
- owner powers;
- mint/burn;
- blacklist/whitelist;
- pausable;
- fee mutability;
- hidden owner;
- supply concentration;
- liquidity lock/burn;
- buy/sell simulation;
- honeypot flag.

---

## Fase 3 — AMM/MEV Scanner

Entrega:

- Uniswap router detection;
- pair detection;
- slippage detector;
- deadline detector;
- swap-and-liquify detector;
- cooldown DoS detector;
- sandwich exposure warning.

---

## Fase 4 — Verified Reports

Entrega:

- workflow de revisão humana;
- triage;
- false positive handling;
- verified seal;
- public URL;
- report versioning;
- scan history.

---

## Fase 5 — Foundry Proof Engine

Entrega:

- geração de PoC;
- fuzz tests;
- invariant tests;
- proof-of-fix;
- CI gate;
- SARIF export para GitHub Security.

---

# 30. Backlog inicial priorizado

## P0 — Essencial

1. Scan por endereço EVM.
2. Upload de arquivos Solidity.
3. AST parser.
4. Detector registry.
5. Finding schema.
6. Severity/status workflow.
7. Security score.
8. Report HTML/PDF.
9. Missing zero address.
10. Missing events.
11. Outdated/floating pragma.
12. ERC20 approve race.
13. Hardcoded address.
14. Unsafe transfer return.
15. Basic gas detectors.

## P1 — Diferencial competitivo

1. Token threat score.
2. Honeypot simulation.
3. Liquidity lock/burn.
4. Owner powers inventory.
5. AMM slippage detectors.
6. Cooldown DoS detector.
7. Reflection accounting detector.
8. Verified report workflow.
9. Public report URL.
10. Noise reduction.

## P2 — Produto premium

1. AI-assisted semantic findings.
2. Foundry PoC generation.
3. Invariant generation.
4. Proof-of-fix.
5. CI/CD GitHub Action.
6. SARIF integration.
7. Human review console.
8. Benchmark corpus.
9. Audit marketplace.
10. Assisted audit reports.

---

# 31. Especificação de qualidade dos detectores

## SPEC-QA-001 — Golden Corpus

Criar corpus com contratos:

- ERC-20 simples seguro;
- ERC-20 com approve race;
- token honeypot;
- token com blacklist;
- token com hidden owner;
- token reflection quebrado;
- token com cooldown DoS;
- token com slippage zero;
- contrato com reentrancy;
- contrato com zero address bug;
- contrato com proxy;
- contrato com NatSpec completo;
- contrato com imports não usados.

## SPEC-QA-002 — Métricas

Cada detector deve ter:

```text
precision_target >= 0.90 para High/Critical
recall_target >= 0.75
false_positive_rate monitorado
runtime_limit por contrato
explainability obrigatória
```

---

# 32. Modelo de spec por detector

Todo detector deve ser definido assim:

```markdown
# DETECTOR SPEC: AMM-COOLDOWN-DOS-001

## Família
AMM/DEX Risk

## Severidade padrão
High

## Problema
Cooldown aplicado ao AMM pair pode bloquear todas as trades.

## Condição de detecção
- contrato identifica AMM pair;
- transfer aplica cooldown quando from ou to é pair;
- pair recebe update em mapping de cooldown;
- transfer subsequente contra o mesmo pair pode reverter.

## Evidência mínima
- variável de cooldown;
- mapping por address;
- função _transfer;
- condição envolvendo AMM pair;
- update de cooldown para pair.

## Falsos positivos
- cooldown não aplicado ao pair;
- pair explicitamente excluído;
- cooldown apenas informativo;
- trade não reverte.

## Remediação
- aplicar cooldown apenas a user address;
- excluir AMM pair do state tracking;
- separar buy/sell cooldown.

## Teste esperado
- primeira compra passa;
- segunda compra por outro usuário dentro da janela não deve ser bloqueada.
```

Esse modelo deve ser repetido para todos os detectores.

---

# 33. Produto final desejado

A plataforma deve se comportar assim:

1. Usuário informa contrato ou repo.
2. Sistema busca código e metadados.
3. Sistema compila ou analisa parcialmente.
4. Detectores estáticos rodam.
5. Detectores token/AMM rodam.
6. Simulações rodam quando aplicável.
7. IA sugere findings semânticos.
8. Findings são normalizados.
9. Score técnico e threat score são calculados.
10. Report draft é gerado.
11. Usuário corrige, marca status ou solicita verificação.
12. Reviewer valida.
13. Report público é publicado.
14. CI/CD monitora regressões futuras.

---

# 34. Minha recomendação estratégica

Para chegar perto da SolidityScan do zero sem tentar copiar tudo de uma vez, eu construiria nesta ordem:

**Primeiro:** scanner estático + report bonito.  
**Segundo:** token risk + honeypot + liquidity.  
**Terceiro:** AMM/MEV + tokenomics complexa.  
**Quarto:** verified reports com revisão humana.  
**Quinto:** Foundry proof-of-fix, que seria nosso diferencial.

A SolidityScan parece forte em **scan, score, report público e token threat analysis**. Mas os reports mostram espaço para melhorar em **redução de ruído, consistência interna, evidência reproduzível e proof-of-fix**. Nossa plataforma deve nascer com esse posicionamento:

> **Não apenas “encontramos vulnerabilities”; nós explicamos, priorizamos, reproduzimos e provamos a correção.**

---

### 👤 USUÁRIO *(03:14:14 UTC)*:

para usarmos e aprofundarmos nossas SPECS no Codex e criarmos nosso MVP de scanner estático + report bonito, qual o passo a passo?

---

### 🤖 ASSISTENTE (ChatGPT) *(03:14:17 UTC)*:

Sim. Eu faria isso em **duas trilhas paralelas**:

1. **Trilha SDD/Codex:** transformar tudo em specs pequenas, versionadas e testáveis.  
2. **Trilha MVP:** implementar um scanner estático simples + relatório bonito em HTML/PDF.

A referência de produto que estamos usando é clara: os reports da SolidityScan têm **Static Scanning**, severidades `Critical`, `High`, `Medium`, `Low`, `Informational` e `Gas`, status como `Fixed`, `Pending Fix` e `Won’t Fix`, além de executive summary, threat summary, findings summary e vulnerability details. fileciteturn0file0 fileciteturn0file1

---

# 1. Escopo correto do MVP

Para o MVP, eu não tentaria fazer “700+ módulos” como eles dizem ter nos reports. A gente deve fazer:

## MVP v0.1

**Entrada:**

- upload de arquivo `.sol`;
- ou pasta local com contratos;
- depois, numa v0.2, endereço EVM verificado via BscScan/Etherscan.

**Processamento:**

- parser Solidity;
- detectores estáticos simples;
- normalização dos achados;
- score;
- geração de relatório.

**Saída:**

- JSON técnico;
- HTML bonito;
- PDF exportável.

## Detectores iniciais

Baseados diretamente nos dois reports:

| ID | Detector | Severidade inicial |
|---|---|---|
| `COMP-001` | Floating pragma | Low |
| `COMP-002` | Outdated compiler version | Low |
| `SEC-001` | Missing zero address validation | Low |
| `SEC-002` | Missing events | Low |
| `ERC-001` | ERC20 approve front-running | Medium |
| `OWN-001` | Hardcoded address detected | Informational/Low |
| `DOC-001` | Missing NatSpec comments | Informational |
| `DOC-002` | Missing `@inheritdoc` | Informational |
| `GAS-001` | Public constants can be private | Gas |
| `GAS-002` | Storage variable caching | Gas |
| `GAS-003` | Unused imports | Gas |
| `GAS-004` | Constructor can be payable | Gas |

Esse conjunto já permite gerar um report parecido com o Centel, que tinha score alto, threat summary moderado e achados principalmente Low/Informational/Gas. fileciteturn0file1

---

# 2. Estrutura de repositório recomendada

Eu criaria o repo assim:

```txt
evm-auditscan/
  apps/
    web/
    api/
    cli/
  packages/
    scanner-core/
    solidity-parser/
    detector-engine/
    report-engine/
    scoring-engine/
    shared-types/
  specs/
    000-product-charter.md
    001-domain-model.md
    010-scan-inputs.md
    020-finding-schema.md
    030-severity-model.md
    040-scoring-model.md
    100-detector-registry.md
    detectors/
      COMP-001-floating-pragma.md
      COMP-002-outdated-compiler.md
      SEC-001-zero-address-validation.md
      SEC-002-missing-events.md
      ERC-001-approve-front-running.md
      OWN-001-hardcoded-address.md
      DOC-001-missing-natspec.md
      GAS-001-public-constants-private.md
    reports/
      001-html-report-layout.md
      002-pdf-report-layout.md
      003-executive-summary.md
      004-findings-summary.md
  fixtures/
    contracts/
      clean-erc20.sol
      floating-pragma.sol
      missing-events.sol
      missing-zero-address.sol
      approve-front-running.sol
      hardcoded-address.sol
  tests/
    scanner/
    detectors/
    report/
  docs/
    architecture.md
    roadmap.md
    detector-authoring-guide.md
  codex/
    realmente.md
    prompts/
      planner.md
      implementer.md
      reviewer.md
      spec-writer.md
      detector-writer.md
```

Para o MVP, eu começaria com **CLI + report HTML**. Web app vem depois.

---

# 3. Stack recomendada

Como o foco é produtividade solo:

## Opção mais simples

- **Node.js + TypeScript**
- `@solidity-parser/parser`
- `commander` para CLI
- `zod` para schemas
- `handlebars` ou `react-email`/`tsx` para templates HTML
- `playwright` para converter HTML em PDF
- `vitest` para testes

## Por que TypeScript?

Porque fica mais fácil integrar depois com:

- frontend Next.js;
- API;
- GitHub Action;
- renderização de report;
- SDK.

A engine de scanner pode começar simples com AST. Depois dá para integrar Slither, solc, Foundry e análise mais profunda.

---

# 4. Primeiro artefato: `000-product-charter.md`

No Codex, peça primeiro para criar esse arquivo. Ele é o contrato do produto.

```md
# SPEC-000 — Product Charter

## Objetivo

Construir uma plataforma de auditoria automatizada para contratos Solidity/EVM, capaz de executar static scanning, classificar achados por severidade, calcular score e gerar relatórios HTML/PDF.

## Fora do escopo do MVP

- auditoria manual;
- análise dinâmica;
- simulação honeypot;
- integração com explorers;
- AI findings;
- verificação humana;
- login/assinatura;
- scan de repositório remoto.

## Escopo do MVP

- scan local de arquivos `.sol`;
- parser AST;
- detectores estáticos iniciais;
- schema normalizado de findings;
- score simples;
- report HTML;
- export PDF;
- fixtures de contratos vulneráveis;
- testes automatizados.
```

---

# 5. Segundo artefato: schema do Finding

Esse é o coração do sistema.

```ts
export type Severity =
  | "Critical"
  | "High"
  | "Medium"
  | "Low"
  | "Informational"
  | "Gas";

export type FindingStatus =
  | "Detected"
  | "Pending Fix"
  | "Fixed"
  | "False Positive"
  | "Won't Fix"
  | "Risk Accepted";

export type DetectionMethod =
  | "AST"
  | "Regex"
  | "StaticRule"
  | "SemanticRule"
  | "Simulation"
  | "AI"
  | "ManualReview";

export interface Finding {
  id: string;
  detectorId: string;
  title: string;
  severity: Severity;
  status: FindingStatus;
  detectionMethod: DetectionMethod;
  confidence: "Low" | "Medium" | "High";
  category: string;
  description: string;
  impact: string;
  recommendation: string;
  filePath: string;
  lineStart?: number;
  lineEnd?: number;
  codeSnippet?: string;
}
```

Os reports da SolidityScan se apoiam muito nesse modelo: severidade, status, método de detecção, instâncias, localização e descrição do achado. O report TokenKickstarter mostra inclusive a coluna `Detection Method`, separando `Automated` e `SolidityScan AI`. fileciteturn0file0

---

# 6. Terceiro artefato: detector spec template

Cada detector precisa nascer de uma spec, não direto do código.

Crie:

```md
# DETECTOR SPEC — COMP-001 Floating Pragma

## Objetivo

Detectar uso de pragma Solidity não fixado, como `^0.8.0`, `>=0.8.0` ou ranges abertos.

## Severidade

Low.

## Racional

Floating pragmas permitem que o contrato seja compilado com versões diferentes da esperada, podendo gerar comportamento inconsistente ou expor o contrato a bugs conhecidos.

## Entrada

Arquivo Solidity parseado.

## Condição de detecção

O detector deve emitir finding quando encontrar:

- `pragma solidity ^x.y.z`;
- `pragma solidity >=x.y.z`;
- `pragma solidity >x.y.z`;
- ranges compostos sem versão fixa.

## Não deve detectar

- `pragma solidity 0.8.24;`
- contratos sem pragma devem ser tratados por outro detector.

## Finding esperado

Title: Use of floating pragma  
Severity: Low  
Category: Compiler  
Detection Method: AST ou Regex  
Status: Detected

## Fixtures

- `fixtures/contracts/floating-pragma.sol`
- `fixtures/contracts/fixed-pragma.sol`

## Critérios de aceite

- Deve detectar `pragma solidity ^0.8.20;`
- Não deve detectar `pragma solidity 0.8.20;`
- Deve retornar linha do pragma.
```

Esse formato vira o padrão para todos os detectores.

---

# 7. Ordem ideal de implementação com Codex

## Passo 1 — Gerar specs base

Prompt para Codex:

```txt
Leia os arquivos em /specs e implemente apenas a estrutura inicial do projeto TypeScript para um scanner estático Solidity/EVM.

Não implemente detectores ainda.

Crie:
- package scanner-core
- package detector-engine
- package shared-types
- package report-engine
- app cli

Inclua:
- tipos Severity, Finding, ScanResult, Detector
- interface Detector
- loader de arquivos .sol
- parser placeholder
- runner de detectores
- saída JSON

Critérios:
- npm test deve passar
- npm run scan fixtures/contracts/example.sol deve retornar um ScanResult válido, mesmo sem findings
```

## Passo 2 — Implementar parser

Prompt:

```txt
Implemente o parser Solidity usando @solidity-parser/parser.

A entrada deve ser um ou mais arquivos .sol.
A saída deve incluir:
- source text
- AST
- lista de pragmas
- lista de contratos
- lista de funções
- lista de eventos
- lista de variáveis de estado
- line/column quando disponível

Adicione testes com fixtures pequenas.
Não implemente detectores nesta etapa.
```

## Passo 3 — Implementar detector registry

Prompt:

```txt
Implemente o Detector Registry conforme specs/100-detector-registry.md.

Cada detector deve ter:
- id
- name
- category
- defaultSeverity
- run(context): Finding[]

Crie mecanismo para registrar detectores e executar todos contra um ScanContext.

Adicione testes garantindo que:
- detectores são registrados
- detectores rodam em ordem determinística
- findings são agregados
- erro em um detector não derruba o scan inteiro
```

## Passo 4 — Implementar 3 detectores fáceis

Comece com:

- Floating pragma;
- Outdated compiler;
- Hardcoded address.

Prompt:

```txt
Implemente os detectores:
- COMP-001 Floating Pragma
- COMP-002 Outdated Compiler Version
- OWN-001 Hardcoded Address

Use as specs em /specs/detectors.
Crie fixtures positivas e negativas.
Cada detector deve retornar Finding normalizado com linha, descrição, impacto e recomendação.

Não altere report-engine ainda.
```

## Passo 5 — Implementar detectores Low/Sec

Depois:

- Missing events;
- Missing zero address validation;
- Unsafe ERC20 transfer return.

Prompt:

```txt
Implemente:
- SEC-001 Missing Zero Address Validation
- SEC-002 Missing Events
- SEC-003 Unsafe ERC20 Transfer Return Value

Priorize heurísticas simples e explícitas.
Marque confidence como Medium quando a análise for heurística.
Adicione testes de falsos positivos básicos.
```

## Passo 6 — Implementar detectores informacionais/gas

Depois:

- Missing NatSpec;
- Public constants can be private;
- Storage variable caching;
- Unused imports;
- Constructor payable.

Esses detectores ajudam a preencher relatório visual, como nos PDFs, onde há grande volume de findings informacionais e gas. O TokenKickstarter, por exemplo, tem 369 informacionais e 214 de gas. fileciteturn0file0

---

# 8. Modelo de CLI do MVP

O primeiro produto usável deve ser CLI:

```bash
auditscan scan ./fixtures/contracts --format json
auditscan scan ./contracts --report html
auditscan scan ./contracts --report pdf
```

Saída esperada:

```txt
EVM AuditScan

Target: ./contracts
Language: Solidity
Methodology: Static Scanning
Security Score: 88.4/100
Findings:
  Critical: 0
  High: 0
  Medium: 1
  Low: 4
  Informational: 12
  Gas: 8

Report generated:
  ./reports/auditscan-report.html
  ./reports/auditscan-report.pdf
```

---

# 9. Scoring simples para o MVP

Não tente acertar uma fórmula perfeita no começo.

Use algo assim:

```ts
const weights = {
  Critical: 25,
  High: 12,
  Medium: 6,
  Low: 2,
  Informational: 0.25,
  Gas: 0.1,
};

score = Math.max(0, 100 - sum(findings.map(f => weights[f.severity])));
```

Depois você normaliza por linhas de código.

A própria SolidityScan diz nos reports que o score é calculado com base em linhas de código e pesos atribuídos a cada issue, dependendo da severidade e confiança. fileciteturn0file0 fileciteturn0file1

---

# 10. Estrutura do report bonito

O report HTML/PDF do MVP deve copiar a lógica, não necessariamente o visual exato.

## Seções

1. **Cover**
2. **Executive Summary**
3. **Security Score**
4. **Findings Summary**
5. **Severity Distribution**
6. **Detector Coverage**
7. **Vulnerability Details**
8. **Gas Optimizations**
9. **Informational Findings**
10. **Scan Metadata**
11. **Disclaimer**

Os PDFs da SolidityScan usam exatamente essa lógica de navegação: classificação e severidade, executive summary, threat summary, findings summary, detalhes e disclaimer. fileciteturn0file0 fileciteturn0file1

---

# 11. Visual do report

Para parecer produto premium, use:

## Componentes

- card grande de score;
- badge de risco;
- gráfico donut de findings;
- tabela de severidades;
- tabela de action taken;
- cards por finding;
- code block com linha afetada;
- recomendação clara;
- tags de categoria;
- status visual.

## Exemplo de estrutura HTML

```html
<section class="cover">
  <p class="eyebrow">Security Assessment Report</p>
  <h1>{{projectName}}</h1>
  <p>{{scanDate}}</p>
  <span class="badge">Static Scanning</span>
</section>

<section class="summary">
  <div class="score-card">
    <span>Security Score</span>
    <strong>{{securityScore}}</strong>
    <p>{{scoreLabel}}</p>
  </div>

  <div class="metrics-grid">
    <div>Critical: {{criticalCount}}</div>
    <div>High: {{highCount}}</div>
    <div>Medium: {{mediumCount}}</div>
    <div>Low: {{lowCount}}</div>
    <div>Info: {{infoCount}}</div>
    <div>Gas: {{gasCount}}</div>
  </div>
</section>
```

## CSS básico

```css
:root {
  --bg: #080d0a;
  --card: #111a15;
  --accent: #6eff7a;
  --text: #f5fff7;
  --muted: #8fa89a;
  --critical: #d62828;
  --high: #f77f00;
  --medium: #fcbf49;
  --low: #52b788;
  --info: #8d99ae;
  --gas: #ffafcc;
}
```

Use uma estética parecida com “security report SaaS”: fundo escuro, verde neon, cards claros para o PDF, gráficos e badges.

---

# 12. Especificação do report engine

Crie:

```md
# SPEC-REPORT-001 — HTML Report

## Objetivo

Gerar um relatório HTML navegável e visualmente premium a partir de um ScanResult.

## Entrada

ScanResult JSON.

## Saída

Arquivo HTML autossuficiente.

## Seções obrigatórias

- Cover
- Executive Summary
- Findings Summary
- Vulnerability Details
- Appendix

## Critérios de aceite

- Deve renderizar mesmo sem findings.
- Deve agrupar findings por severidade.
- Deve ordenar findings por Critical > High > Medium > Low > Informational > Gas.
- Deve exibir score.
- Deve exibir contagem por severidade.
- Deve exibir descrição, impacto e recomendação de cada finding.
```

Depois:

```md
# SPEC-REPORT-002 — PDF Export

## Objetivo

Converter o HTML em PDF usando Playwright.

## Critérios de aceite

- Deve gerar PDF em A4.
- Deve preservar cores, cards e tabelas.
- Deve incluir page breaks entre seções principais.
- Deve salvar em `/reports/{scanId}.pdf`.
```

---

# 13. Como usar Codex sem se perder

Você deve trabalhar em ciclos pequenos:

## Ciclo padrão

1. Escrever spec.
2. Pedir plano.
3. Aprovar plano.
4. Implementar só aquela spec.
5. Rodar testes.
6. Gerar diff.
7. Atualizar `realmente.md`.
8. Próxima spec.

## Prompt padrão para Codex

```txt
Você está trabalhando no projeto evm-auditscan.

Leia:
- codex/realmente.md
- specs/000-product-charter.md
- specs/020-finding-schema.md
- specs/detectors/COMP-001-floating-pragma.md

Tarefa:
implementar apenas o detector COMP-001.

Restrições:
- não alterar arquitetura fora do necessário
- não implementar outros detectores
- criar fixtures positiva e negativa
- criar testes unitários
- atualizar o detector registry
- garantir que npm test passe

Ao final:
- explique arquivos alterados
- liste decisões técnicas
- liste próximos passos
```

Esse formato impede o Codex de sair implementando metade da plataforma de uma vez.

---

# 14. Arquivo `codex/realmente.md`

Esse arquivo deve ser o “estado canônico” depois de compactar contexto.

```md
# Realmente — Estado do Projeto

## Produto

Estamos criando uma plataforma de auditoria automatizada para contratos Solidity/EVM, inspirada em reports estilo SolidityScan.

## MVP atual

Scanner estático local + report HTML/PDF.

## Fora do escopo atual

- login
- billing
- scans por explorer
- IA
- verified reports
- honeypot simulation
- análise dinâmica

## Stack

- TypeScript
- Node.js
- @solidity-parser/parser
- Vitest
- Playwright para PDF
- Handlebars ou TSX para HTML

## Entidades principais

- ScanTarget
- ScanRun
- Detector
- Finding
- ScanResult
- Report

## Severidades

Critical, High, Medium, Low, Informational, Gas.

## Status

Detected, Pending Fix, Fixed, False Positive, Won't Fix, Risk Accepted.

## Detectores MVP

- COMP-001 Floating Pragma
- COMP-002 Outdated Compiler Version
- SEC-001 Missing Zero Address Validation
- SEC-002 Missing Events
- ERC-001 Approve Front-Running
- OWN-001 Hardcoded Address
- DOC-001 Missing NatSpec
- GAS-001 Public Constants Can Be Private
- GAS-002 Storage Variable Caching
- GAS-003 Unused Imports

## Próxima tarefa

[preencher antes de compactar]
```

---

# 15. Checklist de MVP pronto

Considere o MVP pronto quando:

```txt
[ ] CLI escaneia uma pasta local
[ ] Parser extrai AST de arquivos Solidity
[ ] Detector registry executa detectores
[ ] Pelo menos 10 detectores funcionam
[ ] Findings têm schema unificado
[ ] Score é calculado
[ ] Report HTML é gerado
[ ] PDF é exportado
[ ] Fixtures positivas e negativas existem
[ ] Testes automatizados passam
[ ] README ensina como rodar
[ ] Exemplo de report está versionado em /examples
```

---

# 16. Ordem prática para os próximos prompts

Eu seguiria exatamente esta sequência no Codex:

## Prompt 1 — Bootstrap

> Crie o monorepo TypeScript com CLI, packages, testes e estrutura de specs.

## Prompt 2 — Domain types

> Implemente os tipos `Finding`, `Detector`, `ScanResult`, `Severity`, `ScanTarget`.

## Prompt 3 — File loader + parser

> Carregue arquivos `.sol` e gere AST usando `@solidity-parser/parser`.

## Prompt 4 — Detector engine

> Crie registry e executor de detectores.

## Prompt 5 — Primeiro detector

> Implemente `COMP-001 Floating Pragma`.

## Prompt 6 — Mais detectores básicos

> Implemente `COMP-002`, `OWN-001`, `DOC-001`.

## Prompt 7 — Detectores de segurança

> Implemente `SEC-001`, `SEC-002`, `ERC-001`.

## Prompt 8 — Detectores de gas

> Implemente `GAS-001`, `GAS-002`, `GAS-003`.

## Prompt 9 — Scoring

> Implemente scoring engine.

## Prompt 10 — HTML report

> Gere report HTML bonito com summary e findings.

## Prompt 11 — PDF export

> Use Playwright para exportar PDF.

## Prompt 12 — README + demo

> Crie fixtures, exemplo de comando e report exemplo.

---

# 17. O que deixar para a v0.2

Depois do MVP:

- scan por endereço Etherscan/BscScan;
- Threat Summary;
- owner powers inventory;
- ERC-20 detection;
- token supply concentration;
- honeypot simulation;
- Uniswap slippage detectors;
- public report URL;
- GitHub Action;
- SARIF export.

A parte de threat summary é importante, mas não para o MVP inicial. Ela aparece forte nos dois reports: source verified, mint/burn, proxy, blacklist, ERC-20, pausable, owner, supply concentration, hardcoded address, liquidity e honeypot. fileciteturn0file0 fileciteturn0file1

---

# 18. Minha recomendação final

Comece pelo menor produto vendável:

> **CLI que escaneia contratos Solidity locais e gera um report HTML/PDF visualmente bonito com 10 detectores estáticos.**

Não comece por dashboard, login, IA, honeypot, tokenomics nem scan de explorer. Isso tudo vem depois.

O diferencial inicial deve ser:

**“Relatório bonito, limpo e explicável para pré-auditoria Solidity.”**

Depois que isso estiver funcionando, a gente aprofunda as specs de:

1. Threat Summary;
2. Token Risk;
3. AMM/DEX;
4. Honeypot;
5. Verified Reports;
6. Foundry proof-of-fix.

---

### 👤 USUÁRIO *(19:18:45 UTC)*:

quero aprofundar agora em quais detector teremos e quais as specs deles

---

### 🤖 ASSISTENTE (ChatGPT) *(19:19:03 UTC)*:

Perfeito. Agora eu dividiria nossos detectores em **3 ondas**:

1. **MVP v0.1 — scanner estático + report bonito**  
   Detectores simples, AST/regex, fáceis de testar, bons para gerar relatório estilo Centel.

2. **v0.2 — token risk / threat summary**  
   Detectores de ERC-20, owner, pausable, mint, blacklist, fees, hardcoded addresses, risco de token.

3. **v0.3 — DeFi/AMM/semânticos**  
   Detectores mais próximos do report TokenKickstarter: cooldown DoS, reflection accounting, early-sell bypass, slippage/MEV, honeypot e liquidez.

A base de severidades deve seguir o modelo dos reports: `Critical`, `High`, `Medium`, `Low`, `Informational` e `Gas`, com status como `Fixed`, `Pending Fix` e `Won’t Fix`. fileciteturn2file0 fileciteturn2file1

---

# 1. Schema padrão de spec para todo detector

Antes da lista, todo detector deve seguir este formato. Esse é o modelo que vamos usar no Codex.

```md
# DETECTOR SPEC — <ID> <Name>

## Família
Compiler | Security | ERC | Ownership | Tokenomics | AMM | Honeypot | Documentation | Gas | Quality

## Objetivo
O que o detector encontra.

## Severidade padrão
Critical | High | Medium | Low | Informational | Gas

## Maturidade
MVP | v0.2 | v0.3 | Research

## Método de detecção
Regex | AST | StaticRule | SemanticRule | Simulation | ChainData | AI-Assisted

## Pré-requisitos
- Source text?
- AST?
- ABI?
- Bytecode?
- Chain data?
- DEX pair?
- Token holders?

## Condição de detecção
Regras positivas.

## Não deve detectar
Regras negativas / falso positivo esperado.

## Evidência mínima
O que precisa aparecer no finding para ele ser publicável.

## Finding esperado
- title
- severity
- category
- description
- impact
- recommendation
- confidence

## Critérios de aceite
Casos que precisam passar nos testes.

## Fixtures
- positive.sol
- negative.sol
- edge-case.sol
```

No código, cada detector deve gerar um `Finding` normalizado:

```ts
export interface Finding {
  id: string;
  detectorId: string;
  title: string;
  severity: Severity;
  status: FindingStatus;
  detectionMethod: DetectionMethod;
  confidence: "Low" | "Medium" | "High";
  category: string;
  description: string;
  impact: string;
  recommendation: string;
  filePath: string;
  lineStart?: number;
  lineEnd?: number;
  codeSnippet?: string;
}
```

---

# 2. MVP v0.1 — detectores obrigatórios

Esses são os detectores que eu implementaria primeiro. Eles cobrem o tipo de report mais simples, parecido com o Centel, que tinha principalmente achados de baixo risco, informacionais e gas, como missing events, missing zero address, outdated compiler, NatSpec, public constants, storage caching e unused imports. fileciteturn2file1

## Lista v0.1

| ID | Detector | Família | Severidade | Método |
|---|---|---|---|---|
| `COMP-001` | Floating Pragma | Compiler | Low | Regex/AST |
| `COMP-002` | Outdated Compiler Version | Compiler | Low | Regex/AST |
| `SEC-001` | Missing Zero Address Validation | Security | Low | AST/Semantic |
| `SEC-002` | Missing Events on Critical State Change | Security | Low | AST/Semantic |
| `SEC-003` | Unsafe ERC20 Transfer Return Value | Security | Low | AST |
| `ERC-001` | ERC20 Approve Front-Running | ERC | Medium | AST |
| `OWN-001` | Hardcoded Address | Ownership | Informational/Low | Regex/AST |
| `DOC-001` | Missing NatSpec Comments | Documentation | Informational | AST/Text |
| `DOC-002` | Missing Inheritdoc on Override | Documentation | Informational | AST/Text |
| `DOC-003` | Missing Indexed Event Parameters | Documentation | Informational | AST |
| `QUAL-001` | Missing State Variable Visibility | Quality | Informational | AST |
| `QUAL-002` | Return Inside Loop | Quality | Informational | AST |
| `QUAL-003` | Block Values as Proxy for Time | Quality | Informational | AST |
| `GAS-001` | Public Constants Can Be Private | Gas | Gas | AST |
| `GAS-002` | Storage Variable Caching in Memory | Gas | Gas | AST/Semantic |
| `GAS-003` | Unused Imports | Gas | Gas | AST |
| `GAS-004` | Constructor Can Be Payable | Gas | Gas | AST |
| `GAS-005` | Array Length Caching | Gas | Gas | AST |
| `GAS-006` | Long Require/Revert Strings | Gas | Gas | AST/Text |
| `GAS-007` | Unnecessary Default Value Initialization | Gas | Gas | AST |
| `GAS-008` | Use of SafeMath in Solidity 0.8+ | Gas | Gas | AST/Import |

O report TokenKickstarter tem exatamente esse padrão de mix: achados High/Medium mais importantes, mas também muitos Informational e Gas, incluindo NatSpec, block values as time, missing indexed keywords, state visibility, array length caching, SafeMath, storage caching, bitmaps e outros. fileciteturn1file9

---

# 3. Specs detalhadas dos detectores MVP

## `COMP-001` — Floating Pragma

```md
# DETECTOR SPEC — COMP-001 Floating Pragma

## Família
Compiler

## Objetivo
Detectar pragmas Solidity não fixados.

## Severidade padrão
Low

## Método
Regex + AST

## Condição de detecção
Emitir finding quando encontrar:
- `pragma solidity ^0.8.0;`
- `pragma solidity >=0.8.0;`
- `pragma solidity >0.8.0;`
- ranges abertos ou compostos sem versão exata.

## Não deve detectar
- `pragma solidity 0.8.24;`
- arquivos sem pragma, pois isso deve ser outro detector.

## Evidência mínima
- linha do pragma;
- texto do pragma;
- versão detectada.

## Finding
Title: Use of Floating Pragma  
Severity: Low  
Category: Compiler  
Confidence: High

## Impacto
O contrato pode ser compilado com uma versão diferente da usada no desenvolvimento, gerando comportamento inesperado ou exposição a bugs de compilador.

## Remediação
Fixar uma versão específica do compilador.

## Fixtures
- `floating-pragma.positive.sol`
- `fixed-pragma.negative.sol`

## Critérios de aceite
- Deve detectar `^0.8.20`.
- Deve detectar `>=0.8.0`.
- Não deve detectar `0.8.20`.
```

---

## `COMP-002` — Outdated Compiler Version

```md
# DETECTOR SPEC — COMP-002 Outdated Compiler Version

## Família
Compiler

## Objetivo
Detectar uso de versão Solidity antiga em relação à baseline configurada.

## Severidade padrão
Low

## Método
Regex + semver

## Configuração
```json
{
  "minimumRecommendedSolc": "0.8.24",
  "latestKnownSolc": "0.8.30"
}
```

## Condição de detecção
Emitir finding quando:
- pragma fixo é menor que `minimumRecommendedSolc`;
- pragma range permite versões antigas;
- versão possui bugs conhecidos na base local `solc-known-bugs.json`.

## Não deve detectar
- contratos fixados em versão igual ou superior à baseline;
- contratos legados marcados explicitamente como `legacyAccepted`.

## Evidência mínima
- versão detectada;
- baseline usada;
- fonte do arquivo.

## Impacto
Versões antigas podem não conter correções de bugs ou melhorias de segurança.

## Remediação
Atualizar para versão estável mais recente compatível com o projeto.
```

Esse detector aparece nos dois reports como recomendação de usar versão mais recente do Solidity. fileciteturn1file5

---

## `SEC-001` — Missing Zero Address Validation

```md
# DETECTOR SPEC — SEC-001 Missing Zero Address Validation

## Família
Security

## Objetivo
Detectar parâmetros `address` usados em operações críticas sem validação contra `address(0)`.

## Severidade padrão
Low

## Método
AST + heurística semântica

## Condição de detecção
Emitir finding quando:
- função recebe parâmetro `address`;
- esse parâmetro é atribuído a variável de estado;
- ou é usado em `_transfer`, `_mint`, `_burn`, `approve`, `setOwner`, `setTreasury`, `setRouter`, `setPair`;
- e não existe validação:
  - `require(addr != address(0))`
  - `if (addr == address(0)) revert`
  - custom error equivalente.

## Não deve detectar
- endereço usado apenas para leitura;
- endereço validado em função interna chamada antes do uso;
- endereço explicitamente permitido como zero, com comentário ou nome como `optionalAddress`.

## Evidência mínima
- nome do parâmetro;
- função;
- linha de uso;
- ausência de check.

## Finding
Title: Missing Zero Address Validation  
Severity: Low  
Category: Security  
Confidence: Medium

## Impacto
Pode permitir configuração acidental de endereço zero, levando a perda de controle, perda de tokens ou falha operacional.

## Remediação
Adicionar validação explícita contra `address(0)`.
```

---

## `SEC-002` — Missing Events on Critical State Change

```md
# DETECTOR SPEC — SEC-002 Missing Events

## Família
Security / Observability

## Objetivo
Detectar funções que alteram estado crítico sem emitir evento.

## Severidade padrão
Low

## Método
AST + heurística semântica

## Estado crítico
- owner/admin;
- treasury;
- router;
- pair;
- fees;
- pause/unpause;
- whitelist;
- blacklist;
- limits;
- cooldown;
- mint/burn;
- supply;
- role assignment.

## Condição de detecção
Emitir finding quando:
- função escreve em variável de estado crítica;
- função é `public` ou `external`;
- função não contém `emit`.

## Não deve detectar
- funções internas;
- constructor, se coberto por detector específico;
- funções que escrevem apenas cache ou contador interno irrelevante;
- funções cujo evento é emitido em função interna chamada.

## Evidência mínima
- variável alterada;
- função;
- sugestão de evento.

## Impacto
Dificulta auditoria, monitoramento on-chain e rastreabilidade de mudanças administrativas.

## Remediação
Emitir eventos em todas as alterações críticas de estado.
```

Missing events aparece no report Centel e também como achado Low no TokenKickstarter, com múltiplas instâncias. fileciteturn2file1 fileciteturn2file0

---

## `SEC-003` — Unsafe ERC20 Transfer Return Value

```md
# DETECTOR SPEC — SEC-003 Unsafe ERC20 Transfer Return Value

## Família
Security / ERC

## Objetivo
Detectar chamadas ERC-20 `transfer`, `transferFrom` ou `approve` cujo retorno booleano é ignorado.

## Severidade padrão
Low

## Método
AST

## Condição de detecção
Emitir finding quando encontrar chamadas como:
- `IERC20(token).transfer(to, amount);`
- `token.transfer(to, amount);`
- `token.transferFrom(from, to, amount);`

e o retorno:
- não é checado;
- não está dentro de `require`;
- não usa `SafeERC20`.

## Não deve detectar
- `SafeERC20.safeTransfer`;
- `require(token.transfer(...))`;
- tokens internos conhecidos que revertem em falha e não retornam bool, se whitelistados.

## Evidência mínima
- chamada;
- token;
- função;
- linha.

## Impacto
Tokens ERC-20 não padronizados podem falhar silenciosamente, causando inconsistência de saldo ou comportamento inesperado.

## Remediação
Usar OpenZeppelin `SafeERC20` ou checar explicitamente o retorno.
```

No TokenKickstarter, o report marca `Unsafe ERC20 Withdrawal Ignores Transfer Return Value` como finding Low gerado por IA/semântico. fileciteturn2file0

---

## `ERC-001` — ERC20 Approve Front-Running

```md
# DETECTOR SPEC — ERC-001 ERC20 Approve Front-Running

## Família
ERC

## Objetivo
Detectar implementação clássica de `approve` que sobrescreve allowance diretamente.

## Severidade padrão
Medium

## Método
AST + ERC20 pattern matching

## Condição de detecção
Emitir finding quando:
- contrato implementa `approve(address spender, uint256 amount)`;
- existe mapping `_allowances`;
- função faz `_allowances[msg.sender][spender] = amount`;
- não exige allowance atual ser zero;
- não oferece mitigação evidente como `increaseAllowance`/`decreaseAllowance`.

## Não deve detectar
- contratos que seguem padrão zero-first:
  `require(amount == 0 || allowance == 0)`;
- contratos que só usam `increaseAllowance` e `decreaseAllowance`;
- wrappers internos sem exposição pública.

## Evidência mínima
- função approve;
- assignment de allowance;
- ausência de mitigação.

## Impacto
O spender pode observar uma alteração de allowance no mempool e usar tanto a allowance antiga quanto a nova.

## Remediação
Implementar `increaseAllowance`/`decreaseAllowance` ou exigir zerar allowance antes de alterar para outro valor não-zero.
```

No TokenKickstarter, o approve front-running aparece como Medium, com 6 instâncias, método Automated. fileciteturn2file0

---

## `OWN-001` — Hardcoded Address

```md
# DETECTOR SPEC — OWN-001 Hardcoded Address

## Família
Ownership / Configuration

## Objetivo
Detectar endereços EVM literais no código.

## Severidade padrão
Informational

## Elevar para Low quando
- endereço é usado como owner/admin;
- treasury;
- router;
- pair;
- token externo;
- privileged address.

## Método
Regex + AST context

## Condição de detecção
Emitir finding quando encontrar literal:
`0x[a-fA-F0-9]{40}`

## Não deve detectar
- `address(0)`;
- burn address conhecida;
- endereços em comentários;
- endereços em testes;
- constantes de rede explicitamente documentadas, se configuração permitir.

## Evidência mínima
- endereço;
- variável/função onde aparece;
- contexto de uso.

## Impacto
Endereços fixos dificultam manutenção, migração, upgrades e podem esconder privilégios.

## Remediação
Mover para configuração, constructor, immutable documentado ou registry.
```

O TokenKickstarter report aponta hardcoded addresses no Threat Summary e também como finding informacional; o Centel report indica que esse tipo de análise faz parte do threat scan. fileciteturn2file0 fileciteturn2file1

---

## `DOC-001` — Missing NatSpec Comments

```md
# DETECTOR SPEC — DOC-001 Missing NatSpec Comments

## Família
Documentation

## Objetivo
Detectar ausência de NatSpec em contratos, funções, modifiers, constructors e variáveis públicas.

## Severidade padrão
Informational

## Método
AST + source comments

## Condição de detecção
Emitir finding quando elemento público/externo não tiver:
- `@notice`;
- `@dev`;
- `@param`;
- `@return`, quando aplicável.

## Não deve detectar
- funções privadas simples;
- getters automáticos;
- interfaces minimalistas, se configuração permitir;
- arquivos de teste.

## Evidência mínima
- tipo do elemento;
- nome;
- NatSpec ausente.

## Impacto
Dificulta auditoria, manutenção, geração de documentação e entendimento público do contrato.

## Remediação
Adicionar comentários NatSpec completos.
```

Esse detector é importante para “encher” a seção informacional do report. No TokenKickstarter, há dezenas de achados NatSpec, incluindo ausência de `@dev`, `@notice`, `@inheritdoc` e descrições de variáveis públicas. fileciteturn1file9

---

## `DOC-002` — Missing Inheritdoc on Override

```md
# DETECTOR SPEC — DOC-002 Missing Inheritdoc on Override

## Família
Documentation

## Objetivo
Detectar funções `override` sem `@inheritdoc`.

## Severidade padrão
Informational

## Método
AST + source comments

## Condição de detecção
Emitir finding quando:
- função contém `override`;
- não há comentário NatSpec imediatamente acima;
- comentário não contém `@inheritdoc`.

## Não deve detectar
- override com NatSpec completo;
- override em arquivos de teste.

## Remediação
Adicionar `/// @inheritdoc InterfaceName`.
```

---

## `DOC-003` — Missing Indexed Event Parameters

```md
# DETECTOR SPEC — DOC-003 Missing Indexed Event Parameters

## Família
Documentation / Observability

## Objetivo
Detectar eventos cujos campos filtráveis não usam `indexed`.

## Severidade padrão
Informational

## Método
AST

## Condição de detecção
Emitir finding quando evento tiver parâmetros `address` relevantes sem `indexed`.

## Heurística de relevância
Nomes como:
- `user`;
- `account`;
- `owner`;
- `spender`;
- `from`;
- `to`;
- `token`;
- `pair`;
- `router`.

## Não deve detectar
- eventos com 3 parâmetros já indexados;
- parâmetros de texto/string;
- valores numéricos menos úteis para filtro.

## Impacto
Dificulta indexação, monitoramento e busca por eventos.
```

---

## `QUAL-001` — Missing State Variable Visibility

```md
# DETECTOR SPEC — QUAL-001 Missing State Variable Visibility

## Família
Code Quality

## Objetivo
Detectar variáveis de estado sem visibilidade explícita.

## Severidade padrão
Informational

## Método
AST

## Condição de detecção
Emitir finding quando uma variável de estado não possuir:
- `public`;
- `private`;
- `internal`.

## Remediação
Adicionar visibilidade explícita.
```

---

## `QUAL-002` — Return Inside Loop

```md
# DETECTOR SPEC — QUAL-002 Return Inside Loop

## Família
Code Quality

## Objetivo
Detectar `return` dentro de loops.

## Severidade padrão
Informational

## Método
AST

## Condição de detecção
Emitir finding quando `ReturnStatement` estiver dentro de:
- `for`;
- `while`;
- `do while`.

## Não deve detectar
- loops com `return` intencional em função de busca, se anotado com `// auditscan-ignore QUAL-002`.

## Impacto
Pode indicar fluxo de controle confuso, resultado parcial ou bug lógico.
```

---

## `QUAL-003` — Block Values as Proxy for Time

```md
# DETECTOR SPEC — QUAL-003 Block Values as Proxy for Time

## Família
Code Quality / Time Risk

## Objetivo
Detectar uso de `block.number` como aproximação de tempo.

## Severidade padrão
Informational

## Método
AST

## Condição de detecção
Emitir finding quando:
- `block.number` aparece em cálculo de tempo;
- variável relacionada contém `time`, `delay`, `cooldown`, `deadline`, `duration`, `period`.

## Remediação
Usar `block.timestamp` com tolerância apropriada, quando tempo real for necessário.
```

---

## `GAS-001` — Public Constants Can Be Private

```md
# DETECTOR SPEC — GAS-001 Public Constants Can Be Private

## Família
Gas

## Objetivo
Detectar constantes públicas que não precisam de getter público.

## Severidade padrão
Gas

## Método
AST

## Condição de detecção
Emitir finding quando:
- variável é `constant`;
- visibilidade é `public`;
- não é usada por interface;
- nome não é parte de padrão ERC, como `name`, `symbol`, `decimals`.

## Remediação
Trocar `public` por `private` ou `internal`, se getter público não for necessário.
```

Esse achado aparece no report Centel como otimização de gas. fileciteturn2file1

---

## `GAS-002` — Storage Variable Caching in Memory

```md
# DETECTOR SPEC — GAS-002 Storage Variable Caching in Memory

## Família
Gas

## Objetivo
Detectar múltiplas leituras da mesma variável de estado dentro de uma função.

## Severidade padrão
Gas

## Método
AST + symbol usage count

## Condição de detecção
Emitir finding quando:
- uma variável de estado é lida mais de uma vez na mesma função;
- não há cache local;
- função não é view trivial.

## Não deve detectar
- variáveis imutáveis;
- constants;
- leituras únicas;
- funções pequenas onde o ganho é irrelevante, se configurado.

## Impacto
`SLOAD` é mais caro do que ler de memória ou stack.

## Remediação
Salvar a variável em variável local quando usada múltiplas vezes.
```

O Centel report descreve esse detector explicitamente: a variável de estado é usada múltiplas vezes e `SLOADs` são mais caros que `MLOAD/MSTORE`. fileciteturn1file1

---

## `GAS-003` — Unused Imports

```md
# DETECTOR SPEC — GAS-003 Unused Imports

## Família
Gas / Quality

## Objetivo
Detectar imports Solidity que não são usados.

## Severidade padrão
Gas

## Método
AST + symbol table

## Condição de detecção
Emitir finding quando:
- arquivo importa símbolo ou arquivo;
- nenhum contrato, library, interface, type ou função importada é referenciada.

## Não deve detectar
- imports globais necessários por side effect, se anotados;
- imports usados em herança;
- imports usados apenas em NatSpec, se configuração permitir.

## Remediação
Remover imports não utilizados.
```

O Centel report também tem `Unused Imports` como gas issue. fileciteturn1file1

---

## `GAS-004` — Constructor Can Be Payable

```md
# DETECTOR SPEC — GAS-004 Constructor Can Be Payable

## Família
Gas

## Objetivo
Sugerir marcar constructor como `payable` para economizar gas no deploy quando não houver restrição necessária.

## Severidade padrão
Gas

## Método
AST

## Condição de detecção
Emitir finding quando:
- constructor não é payable;
- constructor não usa `msg.value`;
- não há necessidade explícita de rejeitar ETH.

## Não deve detectar
- contracts que intencionalmente não aceitam ETH;
- constructor com lógica que depende de `msg.value == 0`.

## Remediação
Declarar `constructor(...) payable`.
```

---

## `GAS-005` — Array Length Caching

```md
# DETECTOR SPEC — GAS-005 Array Length Caching

## Família
Gas

## Objetivo
Detectar loops que leem `.length` repetidamente.

## Severidade padrão
Gas

## Método
AST

## Condição de detecção
Emitir finding quando:
- loop usa `i < array.length`;
- array é storage ou calldata;
- `.length` é lido a cada iteração.

## Remediação
Cachear `uint256 len = array.length;`.
```

---

## `GAS-006` — Long Require/Revert Strings

```md
# DETECTOR SPEC — GAS-006 Long Require/Revert Strings

## Família
Gas

## Objetivo
Detectar strings longas em `require` ou `revert`.

## Severidade padrão
Gas

## Método
AST/Text

## Condição de detecção
Emitir finding quando:
- string literal em require/revert ultrapassa threshold, ex. 32 ou 64 bytes.

## Remediação
Usar custom errors.
```

---

## `GAS-007` — Unnecessary Default Value Initialization

```md
# DETECTOR SPEC — GAS-007 Unnecessary Default Value Initialization

## Família
Gas

## Objetivo
Detectar inicialização explícita com valor default.

## Severidade padrão
Gas

## Exemplos
- `uint256 x = 0;`
- `bool active = false;`
- `address a = address(0);`

## Remediação
Remover inicialização redundante.
```

---

## `GAS-008` — Use of SafeMath in Solidity 0.8+

```md
# DETECTOR SPEC — GAS-008 Use of SafeMath in Solidity 0.8+

## Família
Gas

## Objetivo
Detectar uso de SafeMath em contratos Solidity 0.8+, onde overflow/underflow já é checado por padrão.

## Severidade padrão
Gas

## Método
Import + using statement + pragma

## Condição de detecção
Emitir finding quando:
- pragma >= 0.8.0;
- há import ou using de SafeMath;
- operações usam `.add`, `.sub`, `.mul`, `.div`.

## Remediação
Remover SafeMath, salvo em casos específicos documentados.
```

---

# 4. v0.2 — detectores de Threat Summary / Token Risk

Essa fase começa a aproximar a plataforma da parte mais forte dos reports: source verified, mint/burn, proxy, blacklist, ERC-20, pausable, owner, supply concentration, cooldown, fees, hardcoded addresses, hidden owner, liquidity, honeypot etc. O TokenKickstarter tem Threat Score `34.1/100`, High Risk, e lista riscos como ERC-20 approve race, supply concentration, cooldown, hardcoded addresses, liquidity not burnt e honeypot. fileciteturn2file0

## Lista v0.2

| ID | Detector | Família | Severidade | Método |
|---|---|---|---|---|
| `TOK-001` | ERC20 Contract Detection | Tokenomics | Info | AST/ABI |
| `TOK-002` | Mint Capability Detection | Tokenomics | Medium/High | AST |
| `TOK-003` | Burn Capability Detection | Tokenomics | Info/Low | AST |
| `TOK-004` | Pausable Contract Detection | Tokenomics | Info/Low | AST |
| `TOK-005` | Blacklist Capability | Tokenomics | Medium | AST/Semantic |
| `TOK-006` | Whitelist / Fee Exclusion Capability | Tokenomics | Low/Medium | AST |
| `TOK-007` | Owner Can Set Fees | Tokenomics | Medium | AST |
| `TOK-008` | Owner/Admin Critical Functions | Ownership | Low/Medium | AST |
| `TOK-009` | Owner Can Modify Balances | Tokenomics | High | AST/Semantic |
| `TOK-010` | Fixed Supply Integrity | Tokenomics | Medium | AST |
| `OWN-002` | Hidden Owner | Ownership | High | AST/Semantic |
| `OWN-003` | Special Access Addresses | Ownership | Medium | AST/Semantic |
| `OWN-004` | Owner Renounced Detection | Ownership | Info | AST/ChainData |
| `OWN-005` | Selfdestruct Capability | Ownership | High | AST |
| `UPG-001` | Proxy / Upgradeability Detection | Upgradeability | Info/Medium | Bytecode/AST |
| `THR-001` | Threat Summary Aggregator | Threat | N/A | Aggregator |
| `CHAIN-001` | Source Code Verification | ChainData | Info | Explorer |
| `CHAIN-002` | Supply Concentration | ChainData | Medium/High | Explorer/RPC |
| `LIQ-001` | Liquidity Burn Status | Liquidity | Medium/High | ChainData |
| `LIQ-002` | Liquidity Lock Status | Liquidity | Medium/High | ChainData |

---

## `TOK-002` — Mint Capability Detection

```md
# DETECTOR SPEC — TOK-002 Mint Capability Detection

## Família
Tokenomics

## Objetivo
Detectar capacidade de criação de novos tokens.

## Severidade padrão
Medium

## Elevar para High quando
- função é pública/externa;
- função é onlyOwner/admin;
- altera total supply;
- não há cap;
- não há evento;
- owner não está renounced.

## Método
AST + semantic matching

## Condição de detecção
Emitir finding quando função:
- chama `_mint`;
- incrementa `_totalSupply`, `totalSupply`, `_tTotal`, `_rTotal`;
- emite `Transfer(address(0), to, amount)`;
- possui nomes como `mint`, `issue`, `createTokens`.

## Não deve detectar
- mint em constructor para supply inicial;
- função interna inacessível;
- mint desabilitado por `require(false)` ou renounced owner, se comprovado.

## Impacto
Mint arbitrário pode inflar supply e diluir holders.

## Remediação
Adicionar cap, timelock, governance, evento e restrições claras; remover se não necessário.
```

---

## `TOK-004` — Pausable Contract Detection

```md
# DETECTOR SPEC — TOK-004 Pausable Contract Detection

## Família
Tokenomics / Availability

## Objetivo
Detectar se o contrato pode pausar transfers, compra, venda ou operações críticas.

## Severidade padrão
Informational

## Elevar para Low/Medium quando
- owner pode pausar trading;
- não há unpause transparente;
- função afeta transferências de usuários;
- não há evento.

## Método
AST

## Condição de detecção
Procurar:
- `paused`;
- `pause`;
- `unpause`;
- `whenNotPaused`;
- `tradingEnabled`;
- `enableTrading`;
- `transferDelayEnabled`.

## Impacto
Pausas podem ser legítimas, mas também podem impedir usuários de negociar ou movimentar fundos.
```

Pausable contract aparece nos Threat Summaries dos dois reports. fileciteturn2file0 fileciteturn2file1

---

## `TOK-005` — Blacklist Capability

```md
# DETECTOR SPEC — TOK-005 Blacklist Capability

## Família
Tokenomics / Ownership

## Objetivo
Detectar capacidade de bloquear usuários, tokens ou transfers.

## Severidade padrão
Medium

## Método
AST + semantic matching

## Condição de detecção
Emitir finding quando:
- existe mapping de blacklist;
- função owner/admin altera esse mapping;
- `_transfer` checa se `from` ou `to` está bloqueado.

## Padrões de nomes
- `blacklist`;
- `isBlacklisted`;
- `blocked`;
- `bots`;
- `isBot`;
- `denylist`;
- `ban`.

## Não deve detectar
- blacklist apenas de contratos maliciosos, se claramente documentado;
- denylist usada só para UI, sem afetar transfer.

## Impacto
Owner/admin pode impedir usuários de transferir ou vender tokens.
```

---

## `TOK-007` — Owner Can Set Fees

```md
# DETECTOR SPEC — TOK-007 Owner Can Set Fees

## Família
Tokenomics

## Objetivo
Detectar se owner/admin pode alterar taxas.

## Severidade padrão
Medium

## Método
AST

## Condição de detecção
Emitir finding quando:
- função onlyOwner/admin altera variáveis com nomes:
  - `fee`
  - `tax`
  - `buyTax`
  - `sellTax`
  - `liquidityFee`
  - `marketingFee`
  - `treasuryFee`
- taxa é usada em `_transfer`.

## Elevar severidade
High se:
- não há limite máximo;
- taxa pode chegar a 100%;
- taxa é alterável sem timelock;
- evento ausente.

## Impacto
Taxas abusivas podem criar honeypot econômico ou confiscar valor em compras/vendas.
```

---

## `OWN-002` — Hidden Owner

```md
# DETECTOR SPEC — OWN-002 Hidden Owner

## Família
Ownership

## Objetivo
Detectar papéis administrativos ocultos que não usam o nome `owner`.

## Severidade padrão
High

## Método
AST + semantic matching

## Condição de detecção
Emitir finding quando:
- variável address/mapping controla acesso;
- modifier compara `msg.sender` com endereço ou mapping;
- nome não é `owner`;
- função protegida altera estado crítico.

## Padrões
- `_auth`;
- `operator`;
- `controller`;
- `executor`;
- `manager`;
- `authorized`;
- `isExcluded`;
- `isFeeExempt`;
- `special`.

## Evidência mínima
- variável de privilégio;
- modifier ou require;
- funções protegidas.

## Remediação
Usar controle de acesso explícito, documentado e auditável.
```

O Threat Summary do TokenKickstarter inclui “No hidden owner detected”, mostrando que esse tipo de detector faz parte do escopo da plataforma-alvo. fileciteturn2file0

---

## `CHAIN-002` — Supply Concentration

```md
# DETECTOR SPEC — CHAIN-002 Supply Concentration

## Família
ChainData / Tokenomics

## Objetivo
Detectar concentração relevante de supply em poucas carteiras.

## Severidade padrão
Medium

## Pré-requisitos
- chain;
- token address;
- total supply;
- top holders via explorer/RPC/indexer.

## Condição de detecção
Emitir finding quando:
- qualquer carteira possui > 5%;
- elevar risco em > 10%;
- High em > 20%;
- Critical/Severe em > 50%, dependendo do contexto.

## Não deve detectar como risco alto
- burn address;
- LP lock;
- vesting contract;
- treasury multisig conhecido, se documentado.

## Impacto
Carteiras concentradas podem manipular preço, despejar tokens ou controlar governança.

## Remediação
Documentar distribuição, vesting, lock, multisig ou queima.
```

Ambos os Threat Summaries verificam endereços com mais de 20% do supply circulante. fileciteturn2file0 fileciteturn2file1

---

# 5. v0.3 — detectores DeFi/AMM/semânticos

Essa é a parte que mais diferencia o report TokenKickstarter do Centel. Ele tem achados de lógica de mercado: cooldown global bloqueando trades AMM, mint quebrando reflection accounting, bypass de early-sell penalty, slippage hardcoded, deadline como `block.timestamp`, swap-and-liquify sem proteção e honeypot. fileciteturn2file0

## Lista v0.3

| ID | Detector | Família | Severidade | Método |
|---|---|---|---|---|
| `AMM-001` | Uniswap Router Detection | AMM | Info | AST |
| `AMM-002` | Hardcoded Slippage for Uniswap | AMM/MEV | Medium | AST |
| `AMM-003` | Uniswap Deadline Set to `block.timestamp` | AMM/MEV | Medium | AST |
| `AMM-004` | SwapAndLiquify Zero Slippage Protection | AMM/MEV | Medium | AST/Semantic |
| `AMM-005` | Pair-Level Cooldown DoS | AMM/Availability | High | Semantic |
| `TOK-011` | Reflection Accounting Integrity | Tokenomics | High | Semantic |
| `TOK-012` | Early-Sell Penalty Bypass | Tokenomics | Medium | Semantic |
| `HNY-001` | Buy Simulation | Honeypot | Info/High | Simulation |
| `HNY-002` | Sell Simulation | Honeypot | High | Simulation |
| `HNY-003` | Transfer Simulation | Honeypot | Medium | Simulation |
| `MEV-001` | Sandwich Exposure via Slippage Zero | MEV | Medium | Semantic |
| `MEV-002` | Price Manipulation During Auto-Liquidity | MEV | Medium | Semantic |

---

## `AMM-002` — Hardcoded Slippage for Uniswap

```md
# DETECTOR SPEC — AMM-002 Hardcoded Slippage for Uniswap

## Família
AMM / MEV

## Objetivo
Detectar slippage fixa ou insegura em swaps Uniswap-like.

## Severidade padrão
Medium

## Método
AST + semantic matching

## Condição de detecção
Emitir finding quando:
- contrato chama router Uniswap-like;
- `amountOutMin` é calculado com percentual fixo;
- slippage não é parâmetro de usuário;
- não usa oracle/quote externo confiável.

## Padrões
- `swapExactTokensForETHSupportingFeeOnTransferTokens`;
- `swapExactETHForTokens`;
- `swapExactTokensForTokens`;
- `addLiquidity`;
- `addLiquidityETH`.

## Não deve detectar
- slippage parametrizada por usuário;
- slippage calculada por TWAP/oracle;
- operações administrativas com valor insignificante e documentadas.

## Impacto
Slippage fixa pode permitir sandwich attack e execução em preço desfavorável.

## Remediação
Permitir slippage configurável, usar deadline válido, quote atualizado e limites mínimos não-zero.
```

O TokenKickstarter report marca hardcoded slippage como Medium. fileciteturn2file0

---

## `AMM-003` — Uniswap Deadline Set to `block.timestamp`

```md
# DETECTOR SPEC — AMM-003 Uniswap Deadline Set to block.timestamp

## Família
AMM / MEV

## Objetivo
Detectar uso de `block.timestamp` diretamente como deadline em swaps.

## Severidade padrão
Medium

## Método
AST

## Condição de detecção
Emitir finding quando:
- chamada para router Uniswap-like usa `block.timestamp` no parâmetro deadline.

## Não deve detectar
- `block.timestamp + userDeadlineDelta`;
- deadline vindo de parâmetro externo validado;
- deadline calculado com margem configurável.

## Impacto
Usar `block.timestamp` como deadline remove a proteção real de expiração da ordem.

## Remediação
Usar deadline futuro parametrizado e validado.
```

Esse achado aparece no TokenKickstarter como Medium. fileciteturn2file0

---

## `AMM-004` — SwapAndLiquify Zero Slippage Protection

```md
# DETECTOR SPEC — AMM-004 SwapAndLiquify Zero Slippage Protection

## Família
AMM / MEV

## Objetivo
Detectar operações automáticas de swap/liquidity com mínimos zerados.

## Severidade padrão
Medium

## Método
AST + semantic matching

## Condição de detecção
Emitir finding quando:
- função tem nome ou padrão `swapAndLiquify`, `swapTokensForEth`, `addLiquidity`;
- chamada usa:
  - `amountOutMin = 0`;
  - `amountTokenMin = 0`;
  - `amountETHMin = 0`.

## Não deve detectar
- ambiente de teste;
- operação sem impacto financeiro;
- mínimo calculado antes e variável não-zero.

## Impacto
Permite execução a preços arbitrariamente ruins, MEV sandwich e manipulação de preço.

## Remediação
Calcular mínimos com base em quote confiável e slippage configurável.
```

No report, esse achado aparece como Medium e método `SolidityScan AI`. fileciteturn2file0

---

## `AMM-005` — Pair-Level Cooldown DoS

```md
# DETECTOR SPEC — AMM-005 Pair-Level Cooldown DoS

## Família
AMM / Availability

## Objetivo
Detectar cooldown aplicado ao próprio par AMM, causando bloqueio global de trades.

## Severidade padrão
High

## Método
SemanticRule

## Pré-requisitos
- identificação de AMM pair;
- identificação de mapping de cooldown;
- análise da função `_transfer`.

## Condição de detecção
Emitir finding quando:
- existe mapping como `_lastTradeTime[address]`;
- `_transfer` checa se `from` ou `to` é AMM pair;
- o código atualiza cooldown tanto de `from` quanto de `to`;
- o pair pode ser gravado no mapping;
- trades subsequentes envolvendo o mesmo pair podem reverter.

## Não deve detectar
- pair explicitamente excluído do cooldown;
- cooldown aplicado apenas ao usuário final;
- cooldown não causa revert;
- cooldown é só métrica/evento.

## Evidência mínima
- mapping de cooldown;
- condição AMM;
- update para `from`/`to`;
- require que pode reverter.

## Impacto
Qualquer usuário pode bloquear temporariamente compras/vendas para todos os outros usuários durante a janela de cooldown.

## Remediação
Não aplicar cooldown ao pair; aplicar somente ao endereço do usuário final.
```

Esse é o primeiro High do report TokenKickstarter: cooldown global pode bloquear todo trading AMM. fileciteturn2file0

---

## `TOK-011` — Reflection Accounting Integrity

```md
# DETECTOR SPEC — TOK-011 Reflection Accounting Integrity

## Família
Tokenomics / Accounting

## Objetivo
Detectar inconsistências em tokens reflection/RFI.

## Severidade padrão
High

## Método
SemanticRule + invariant template

## Pré-requisitos
Detectar variáveis ou padrões:
- `_rTotal`;
- `_tTotal`;
- `_rOwned`;
- `_tOwned`;
- `_isExcluded`;
- `_getRate`;
- `reflectionFromToken`.

## Condição de detecção
Emitir finding quando:
- função altera `_tTotal`;
- recalcula `_rTotal`;
- não ajusta `_rOwned` proporcionalmente;
- mint para excluded address não atualiza `_tOwned`;
- supply/reflection rate pode distorcer saldos.

## Não deve detectar
- mint apenas em constructor;
- contratos sem reflection;
- alteração de reflection acompanhada de rebalanceamento consistente.

## Evidência mínima
- função que altera supply;
- variáveis reflection alteradas;
- ausência de atualização proporcional.

## Impacto
Pode inflar ou deflacionar balances de holders e quebrar accounting do token.

## Remediação
Não recalcular reflection supply globalmente em mint; atualizar estruturas refletidas e excluídas de forma consistente.

## Teste recomendado
Gerar invariant:
- mint não deve alterar saldo de holders existentes fora do esperado;
- soma efetiva de balances deve permanecer consistente com total supply.
```

Esse é o segundo High do TokenKickstarter: mint recalcula reflection supply e quebra accounting. fileciteturn2file0

---

## `TOK-012` — Early-Sell Penalty Bypass

```md
# DETECTOR SPEC — TOK-012 Early-Sell Penalty Bypass

## Família
Tokenomics

## Objetivo
Detectar bypass de penalidade de venda antecipada via transferência para endereço novo.

## Severidade padrão
Medium

## Método
SemanticRule

## Condição de detecção
Emitir finding quando:
- existe mapping de acquisition time por endereço;
- timestamp é definido apenas em compras vindas do AMM pair;
- penalidade de venda depende de `_tokenAcquisitionTime[from]`;
- transferências entre usuários não propagam acquisition time.

## Não deve detectar
- acquisition time propagado em transfer;
- penalty baseada em lote/tokenId/accounting granular;
- penalty aplicada independentemente do timestamp.

## Impacto
Usuário pode comprar, transferir para wallet nova e vender sem pagar penalidade.

## Remediação
Propagar acquisition time em transferências ou calcular penalidade com base em origem econômica dos tokens.
```

Esse achado aparece como Medium no TokenKickstarter. fileciteturn2file0

---

# 6. Detectores clássicos de segurança que eu colocaria na v0.4

Esses não apareceram como destaque nos dois PDFs, mas uma plataforma de auditoria EVM precisa deles para ser minimamente séria.

| ID | Detector | Severidade |
|---|---|---|
| `SEC-004` | Reentrancy Risk | High/Critical |
| `SEC-005` | `tx.origin` Authorization | High |
| `SEC-006` | Unchecked Low-Level Call | Medium/High |
| `SEC-007` | Arbitrary External Call | High |
| `SEC-008` | Delegatecall to User-Controlled Address | Critical |
| `SEC-009` | Unprotected Initializer | High |
| `SEC-010` | Missing Access Control | High |
| `SEC-011` | Dangerous Selfdestruct | High |
| `SEC-012` | Timestamp Dependence in Critical Logic | Medium |
| `SEC-013` | Signature Replay / Missing ChainId | High |
| `SEC-014` | Weak Randomness | Medium/High |
| `SEC-015` | Integer Division Precision Loss | Medium |
| `SEC-016` | Oracle Price Manipulation Risk | High |
| `UPG-002` | Storage Layout Collision in Upgradeable Contract | Critical |
| `UPG-003` | Uninitialized Implementation Contract | High |

Eu não colocaria esses no primeiro MVP se a meta for entregar rápido o scanner + report. Mas colocaria no roadmap público.

---

# 7. Organização dos arquivos de specs

No repositório:

```txt
specs/
  detectors/
    compiler/
      COMP-001-floating-pragma.md
      COMP-002-outdated-compiler.md

    security/
      SEC-001-missing-zero-address-validation.md
      SEC-002-missing-events.md
      SEC-003-unsafe-erc20-transfer-return.md

    erc/
      ERC-001-approve-front-running.md

    ownership/
      OWN-001-hardcoded-address.md
      OWN-002-hidden-owner.md
      OWN-003-special-access-addresses.md

    tokenomics/
      TOK-001-erc20-detection.md
      TOK-002-mint-capability.md
      TOK-004-pausable-contract.md
      TOK-011-reflection-accounting-integrity.md
      TOK-012-early-sell-penalty-bypass.md

    amm/
      AMM-002-hardcoded-slippage.md
      AMM-003-uniswap-deadline-block-timestamp.md
      AMM-004-zero-slippage-swap-and-liquify.md
      AMM-005-pair-level-cooldown-dos.md

    documentation/
      DOC-001-missing-natspec.md
      DOC-002-missing-inheritdoc.md
      DOC-003-missing-indexed-event-parameters.md

    gas/
      GAS-001-public-constants-private.md
      GAS-002-storage-variable-caching.md
      GAS-003-unused-imports.md
      GAS-004-constructor-payable.md
      GAS-005-array-length-caching.md
```

---

# 8. Detector interface no código

```ts
export interface Detector {
  id: string;
  name: string;
  family: DetectorFamily;
  defaultSeverity: Severity;
  maturity: "MVP" | "V0_2" | "V0_3" | "RESEARCH";
  run(context: ScanContext): Promise<Finding[]> | Finding[];
}
```

```ts
export interface ScanContext {
  files: SourceFile[];
  asts: ParsedSolidityFile[];
  contracts: ContractInfo[];
  symbols: SymbolTable;
  config: ScannerConfig;
}
```

---

# 9. Critério para um detector entrar no MVP

Um detector entra no MVP se atender a pelo menos 4 dos 5 critérios:

```txt
[ ] Pode ser implementado com AST/regex simples
[ ] Gera poucos falsos positivos
[ ] Aparece nos reports analisados
[ ] Melhora a aparência/utilidade do report
[ ] É fácil criar fixture positiva e negativa
```

Por isso, os primeiros devem ser:

1. `COMP-001`
2. `COMP-002`
3. `OWN-001`
4. `SEC-001`
5. `SEC-002`
6. `DOC-001`
7. `DOC-002`
8. `GAS-001`
9. `GAS-002`
10. `GAS-003`

---

# 10. Prompt para o Codex criar as specs

Use este prompt:

```txt
Leia o arquivo specs/000-product-charter.md e crie as specs dos detectores MVP em specs/detectors.

Detectores:
- COMP-001 Floating Pragma
- COMP-002 Outdated Compiler Version
- SEC-001 Missing Zero Address Validation
- SEC-002 Missing Events
- SEC-003 Unsafe ERC20 Transfer Return Value
- ERC-001 Approve Front-Running
- OWN-001 Hardcoded Address
- DOC-001 Missing NatSpec Comments
- DOC-002 Missing Inheritdoc on Override
- DOC-003 Missing Indexed Event Parameters
- GAS-001 Public Constants Can Be Private
- GAS-002 Storage Variable Caching in Memory
- GAS-003 Unused Imports
- GAS-004 Constructor Can Be Payable
- GAS-005 Array Length Caching
- GAS-006 Long Require/Revert Strings
- GAS-007 Unnecessary Default Value Initialization
- GAS-008 Use of SafeMath in Solidity 0.8+

Para cada detector, use exatamente este template:
- Família
- Objetivo
- Severidade padrão
- Maturidade
- Método de detecção
- Pré-requisitos
- Condição de detecção
- Não deve detectar
- Evidência mínima
- Finding esperado
- Impacto
- Remediação
- Fixtures
- Critérios de aceite

Não implemente código ainda.
Apenas crie os arquivos markdown das specs.
```

---

# 11. Minha recomendação prática

Para não virar um monstro impossível, eu fecharia agora o **Detector Backlog v0.1** com 18 detectores:

```txt
COMP-001 Floating Pragma
COMP-002 Outdated Compiler Version
SEC-001 Missing Zero Address Validation
SEC-002 Missing Events
SEC-003 Unsafe ERC20 Transfer Return Value
ERC-001 Approve Front-Running
OWN-001 Hardcoded Address
DOC-001 Missing NatSpec Comments
DOC-002 Missing Inheritdoc on Override
DOC-003 Missing Indexed Event Parameters
QUAL-001 Missing State Variable Visibility
QUAL-002 Return Inside Loop
QUAL-003 Block Values as Proxy for Time
GAS-001 Public Constants Can Be Private
GAS-002 Storage Variable Caching in Memory
GAS-003 Unused Imports
GAS-004 Constructor Can Be Payable
GAS-005 Array Length Caching
```

Com isso, já conseguimos gerar um report visual com:

- score;
- classificação;
- severidade;
- contagem por categoria;
- detalhes de findings;
- recomendações;
- apêndice de gas/documentação;
- aparência parecida com um produto real.

Depois, a v0.2 entra com Threat Summary e Token Risk. Aí sim começamos a ficar próximos da parte mais valiosa da SolidityScan.

---

### 👤 USUÁRIO *(19:27:10 UTC)*:

devo seguir algum formato de filename / estrutura de projeto específico para SPECs e artefatos de documentação e schema?

---

### 🤖 ASSISTENTE (ChatGPT) *(19:27:15 UTC)*:

Sim. Para o Codex funcionar bem em **Spec Driven Development**, eu recomendo seguir uma estrutura bem rígida, com:

1. **IDs estáveis**
2. **filenames previsíveis**
3. **specs pequenas**
4. **schemas separados**
5. **artefatos de documentação separados de specs executáveis**
6. **índice central para o Codex saber o que existe**

A regra principal é:

> **Toda feature, detector, schema e relatório precisa ter um ID único, versionável e rastreável.**

---

# Estrutura recomendada do projeto

```txt
evm-auditscan/
  README.md
  package.json
  turbo.json

  apps/
    cli/
    api/
    web/

  packages/
    scanner-core/
    detector-engine/
    report-engine/
    scoring-engine/
    solidity-parser/
    shared-types/

  specs/
    README.md
    SPEC-000-product-charter.md
    SPEC-001-domain-model.md
    SPEC-002-glossary.md
    SPEC-003-non-goals.md

    architecture/
      ARCH-001-system-overview.md
      ARCH-002-scan-pipeline.md
      ARCH-003-detector-engine.md
      ARCH-004-report-engine.md
      ARCH-005-storage-model.md

    schemas/
      SCHEMA-001-finding.md
      SCHEMA-002-scan-result.md
      SCHEMA-003-detector.md
      SCHEMA-004-report.md
      SCHEMA-005-score.md

    detectors/
      compiler/
        DET-COMP-001-floating-pragma.md
        DET-COMP-002-outdated-compiler-version.md

      security/
        DET-SEC-001-missing-zero-address-validation.md
        DET-SEC-002-missing-events.md
        DET-SEC-003-unsafe-erc20-transfer-return-value.md

      erc/
        DET-ERC-001-approve-front-running.md

      ownership/
        DET-OWN-001-hardcoded-address.md
        DET-OWN-002-hidden-owner.md

      documentation/
        DET-DOC-001-missing-natspec-comments.md
        DET-DOC-002-missing-inheritdoc-on-override.md
        DET-DOC-003-missing-indexed-event-parameters.md

      gas/
        DET-GAS-001-public-constants-can-be-private.md
        DET-GAS-002-storage-variable-caching-in-memory.md
        DET-GAS-003-unused-imports.md
        DET-GAS-004-constructor-can-be-payable.md
        DET-GAS-005-array-length-caching.md

      tokenomics/
        DET-TOK-001-erc20-contract-detection.md
        DET-TOK-002-mint-capability-detection.md
        DET-TOK-003-pausable-contract-detection.md

      amm/
        DET-AMM-001-uniswap-router-detection.md
        DET-AMM-002-hardcoded-slippage-for-uniswap.md
        DET-AMM-003-uniswap-deadline-set-to-block-timestamp.md
        DET-AMM-004-zero-slippage-swap-and-liquify.md
        DET-AMM-005-pair-level-cooldown-dos.md

    reports/
      REPORT-001-html-report-layout.md
      REPORT-002-pdf-report-layout.md
      REPORT-003-executive-summary.md
      REPORT-004-findings-summary.md
      REPORT-005-vulnerability-details.md
      REPORT-006-disclaimer.md

    scoring/
      SCORE-001-security-score.md
      SCORE-002-threat-score.md
      SCORE-003-score-labels.md

    workflows/
      WF-001-local-scan.md
      WF-002-generate-report.md
      WF-003-triage-findings.md
      WF-004-publish-report.md
      WF-005-verified-report.md

  schemas/
    json/
      finding.schema.json
      scan-result.schema.json
      detector.schema.json
      report.schema.json
      score.schema.json

    examples/
      finding.example.json
      scan-result.example.json
      report.example.json

  docs/
    architecture.md
    detector-authoring-guide.md
    report-design-guide.md
    codex-workflow.md
    roadmap.md

  decisions/
    ADR-001-use-typescript.md
    ADR-002-use-solidity-parser.md
    ADR-003-start-with-static-analysis.md
    ADR-004-report-html-before-webapp.md

  fixtures/
    contracts/
      positive/
      negative/
      edge-cases/

  examples/
    reports/
      sample-report.html
      sample-report.pdf
      sample-scan-result.json

  codex/
    realmente.md
    INDEX.md
    prompts/
      001-plan-from-spec.md
      002-implement-detector.md
      003-review-against-spec.md
      004-update-docs.md
      005-generate-tests.md
```

---

# Convenção de nomes

Eu usaria esta regra:

```txt
<TIPO>-<DOMINIO>-<NUMERO>-<slug-em-kebab-case>.md
```

Exemplos:

```txt
DET-SEC-001-missing-zero-address-validation.md
DET-GAS-002-storage-variable-caching-in-memory.md
SCHEMA-001-finding.md
REPORT-004-findings-summary.md
ARCH-002-scan-pipeline.md
WF-003-triage-findings.md
ADR-001-use-typescript.md
```

Para specs globais, pode ser:

```txt
SPEC-000-product-charter.md
SPEC-001-domain-model.md
SPEC-002-glossary.md
SPEC-003-non-goals.md
```

---

# Prefixos recomendados

| Prefixo | Uso |
|---|---|
| `SPEC` | Especificações globais do produto |
| `ARCH` | Arquitetura |
| `DET` | Detectores |
| `SCHEMA` | Schemas conceituais |
| `REPORT` | Especificações de relatório |
| `SCORE` | Regras de score |
| `WF` | Workflows |
| `ADR` | Decisões arquiteturais |
| `QA` | Estratégia de testes |
| `MIG` | Migrações futuras |
| `API` | Endpoints e contratos HTTP |
| `CLI` | Comandos da CLI |

---

# Domínios dos detectores

Para os detectores, eu manteria estes domínios:

| Domínio | Prefixo | Exemplo |
|---|---|---|
| Compiler | `COMP` | `DET-COMP-001-floating-pragma.md` |
| Security | `SEC` | `DET-SEC-001-missing-zero-address-validation.md` |
| ERC Standards | `ERC` | `DET-ERC-001-approve-front-running.md` |
| Ownership | `OWN` | `DET-OWN-001-hardcoded-address.md` |
| Tokenomics | `TOK` | `DET-TOK-002-mint-capability-detection.md` |
| AMM/DEX | `AMM` | `DET-AMM-005-pair-level-cooldown-dos.md` |
| Honeypot | `HNY` | `DET-HNY-001-sell-simulation.md` |
| MEV | `MEV` | `DET-MEV-001-sandwich-exposure.md` |
| Documentation | `DOC` | `DET-DOC-001-missing-natspec-comments.md` |
| Gas | `GAS` | `DET-GAS-001-public-constants-can-be-private.md` |
| Code Quality | `QUAL` | `DET-QUAL-001-return-inside-loop.md` |
| Upgradeability | `UPG` | `DET-UPG-001-proxy-detection.md` |
| Chain Data | `CHAIN` | `DET-CHAIN-001-source-code-verification.md` |
| Liquidity | `LIQ` | `DET-LIQ-001-liquidity-burn-status.md` |

---

# Formato interno de cada SPEC

Toda spec deve começar com frontmatter. Isso ajuda muito o Codex, porque ele consegue localizar status, prioridade, dependências e dono da spec.

```md
---
id: DET-SEC-001
title: Missing Zero Address Validation
type: detector
domain: security
status: draft
maturity: mvp
priority: p0
version: 0.1.0
owner: audit-engine
depends_on:
  - SCHEMA-001
  - ARCH-003
related:
  - DET-SEC-002
  - DET-OWN-001
implementation_package: packages/detector-engine
test_fixture_path: fixtures/contracts/security/missing-zero-address/
---

# DET-SEC-001 — Missing Zero Address Validation

## Objetivo

Detectar parâmetros `address` usados em operações críticas sem validação contra `address(0)`.

## Escopo

Incluído:
- setters administrativos;
- funções de mint;
- funções de transfer;
- configuração de owner, treasury, router e pair.

Fora do escopo:
- endereços opcionais;
- endereços usados apenas para leitura;
- validações feitas em bibliotecas externas ainda não analisadas.

## Severidade padrão

Low.

## Método de detecção

AST + heurística semântica.

## Condição de detecção

Emitir finding quando:
- função recebe parâmetro `address`;
- parâmetro é usado em operação crítica;
- não existe validação explícita contra `address(0)`.

## Não deve detectar

- `require(addr != address(0))`;
- `if (addr == address(0)) revert InvalidAddress();`;
- endereço usado apenas em leitura;
- parâmetro com nome `optionalAddress`, se configurado.

## Evidência mínima

O finding deve conter:
- arquivo;
- função;
- parâmetro;
- linha de uso;
- recomendação.

## Finding esperado

```json
{
  "detectorId": "DET-SEC-001",
  "title": "Missing Zero Address Validation",
  "severity": "Low",
  "category": "Security",
  "confidence": "Medium",
  "status": "Detected"
}
```

## Impacto

Configurar endereço zero pode causar perda de controle, travamento de funcionalidade ou envio irreversível de tokens.

## Remediação

Adicionar validação explícita contra `address(0)`.

## Critérios de aceite

- Deve detectar setter de treasury sem validação.
- Não deve detectar setter com `require(addr != address(0))`.
- Deve retornar linha e trecho de código.
- Deve gerar exatamente um finding por parâmetro vulnerável.

## Fixtures

```txt
fixtures/contracts/security/missing-zero-address/
  positive-set-treasury.sol
  negative-validated-treasury.sol
  edge-optional-address.sol
```
```

---

# Status das specs

Use um lifecycle simples:

```txt
draft → accepted → implemented → verified → deprecated
```

| Status | Significado |
|---|---|
| `draft` | Ainda está sendo pensada |
| `accepted` | Pode ser implementada |
| `implemented` | Código existe |
| `verified` | Testes passam e comportamento bate com a spec |
| `deprecated` | Não usar mais |
| `rejected` | Decidimos não implementar |

O Codex deve ser instruído a **nunca implementar spec em `draft`**, exceto quando você pedir explicitamente.

---

# Prioridade

Use prioridade separada de maturidade:

| Campo | Valores |
|---|---|
| `priority` | `p0`, `p1`, `p2`, `p3` |
| `maturity` | `mvp`, `v0.2`, `v0.3`, `research` |

Exemplo:

```yaml
priority: p0
maturity: mvp
```

Isso significa: entra no MVP e é essencial.

Outro exemplo:

```yaml
priority: p1
maturity: v0.3
```

Significa: importante, mas não agora.

---

# O que deve ficar em `specs/` vs `docs/`

Essa separação é importante.

## `specs/`

Ficam documentos normativos, usados para implementação:

```txt
O sistema deve...
O detector deve...
O report deve...
O schema deve...
Critérios de aceite...
```

## `docs/`

Ficam documentos explicativos:

```txt
Como rodar
Como contribuir
Como criar detector
Visão geral da arquitetura
Guia para usuários
Roadmap textual
```

## `decisions/`

Ficam decisões arquiteturais:

```txt
Por que TypeScript?
Por que começar com CLI?
Por que HTML antes de PDF?
Por que AST antes de Slither?
```

## `schemas/`

Ficam schemas reais consumidos pelo código:

```txt
finding.schema.json
scan-result.schema.json
report.schema.json
```

## `specs/schemas/`

Ficam as specs humanas dos schemas:

```txt
SCHEMA-001-finding.md
SCHEMA-002-scan-result.md
```

Ou seja:

```txt
specs/schemas/SCHEMA-001-finding.md      # explicação humana
schemas/json/finding.schema.json         # contrato técnico validável
```

---

# Estrutura de schemas

Eu usaria JSON Schema para contratos entre scanner, report engine e API.

```txt
schemas/
  json/
    finding.schema.json
    scan-result.schema.json
    detector.schema.json
    report.schema.json
    score.schema.json

  examples/
    finding.example.json
    scan-result.example.json
    report.example.json

  generated/
    finding.d.ts
    scan-result.d.ts
```

Exemplo de filename:

```txt
finding.schema.json
scan-result.schema.json
report.schema.json
```

Não colocaria ID no filename dos schemas técnicos, porque o código vai importar por nome estável. O ID fica dentro do schema:

```json
{
  "$id": "https://evm-auditscan.local/schemas/finding.schema.json",
  "title": "Finding",
  "type": "object"
}
```

---

# Manifest central das specs

Crie um arquivo:

```txt
specs/MANIFEST.yaml
```

Exemplo:

```yaml
version: 0.1.0

specs:
  - id: SPEC-000
    path: specs/SPEC-000-product-charter.md
    status: accepted

  - id: SCHEMA-001
    path: specs/schemas/SCHEMA-001-finding.md
    status: accepted
    outputs:
      - schemas/json/finding.schema.json

  - id: DET-COMP-001
    path: specs/detectors/compiler/DET-COMP-001-floating-pragma.md
    status: accepted
    implementation:
      - packages/detector-engine/src/detectors/compiler/floatingPragma.ts
    tests:
      - packages/detector-engine/src/detectors/compiler/floatingPragma.test.ts
    fixtures:
      - fixtures/contracts/compiler/floating-pragma/

  - id: DET-SEC-001
    path: specs/detectors/security/DET-SEC-001-missing-zero-address-validation.md
    status: draft
```

Esse arquivo é ouro para o Codex. Ele vira o mapa de navegação do projeto.

---

# Estrutura de implementation files

Para manter rastreabilidade, o código deve espelhar os domínios das specs.

```txt
packages/detector-engine/src/detectors/
  compiler/
    floatingPragma.detector.ts
    outdatedCompilerVersion.detector.ts

  security/
    missingZeroAddressValidation.detector.ts
    missingEvents.detector.ts
    unsafeErc20TransferReturnValue.detector.ts

  erc/
    approveFrontRunning.detector.ts

  gas/
    publicConstantsCanBePrivate.detector.ts
```

Teste espelhado:

```txt
packages/detector-engine/src/detectors/
  compiler/
    floatingPragma.detector.test.ts
```

Cada arquivo deve referenciar o ID da spec:

```ts
export const floatingPragmaDetector: Detector = {
  id: "DET-COMP-001",
  name: "Floating Pragma",
  family: "compiler",
  defaultSeverity: "Low",
  run(context) {
    // ...
  },
};
```

---

# Estrutura de fixtures

Use uma pasta por detector:

```txt
fixtures/contracts/
  compiler/
    floating-pragma/
      positive-floating-caret.sol
      positive-open-range.sol
      negative-fixed-version.sol

  security/
    missing-zero-address/
      positive-set-owner.sol
      positive-set-treasury.sol
      negative-require-not-zero.sol
      negative-custom-error.sol

  gas/
    storage-variable-caching/
      positive-repeated-sload.sol
      negative-local-cache.sol
```

Evite nomes genéricos como:

```txt
test1.sol
bug.sol
contract.sol
```

Use nomes que expliquem o caso.

---

# Convenção para exemplos de report

```txt
examples/
  reports/
    report-centel-like.html
    report-centel-like.pdf
    report-token-risk-like.html
    report-token-risk-like.pdf

  scan-results/
    centel-like.scan-result.json
    token-risk-like.scan-result.json
```

Como os reports da SolidityScan usam uma estrutura com capa, classificação de severidade, executive summary, threat summary, findings summary e vulnerability details, nossos exemplos devem seguir essa organização desde o começo. fileciteturn0file0 fileciteturn0file1

---

# Convenção para ADRs

Use:

```txt
decisions/ADR-001-use-typescript.md
decisions/ADR-002-start-with-cli.md
decisions/ADR-003-use-ast-before-slither.md
decisions/ADR-004-generate-html-before-pdf.md
```

Template:

```md
# ADR-001 — Use TypeScript

## Status

accepted

## Contexto

Precisamos construir scanner, CLI, report engine e futuro web app com alta velocidade.

## Decisão

Usar TypeScript no MVP.

## Consequências positivas

- Integra fácil com Next.js.
- Bom para schemas e tipos.
- Fácil gerar CLI e report.

## Consequências negativas

- Análise Solidity profunda pode exigir integração posterior com ferramentas Python/Rust.

## Alternativas consideradas

- Python
- Rust
- Go
```

---

# Convenção para prompts do Codex

```txt
codex/prompts/
  001-bootstrap-project.md
  002-implement-domain-types.md
  003-implement-parser.md
  004-implement-detector-registry.md
  005-implement-detector.md
  006-review-against-spec.md
  007-generate-report-engine.md
```

Cada prompt deve declarar:

```md
# Prompt — Implement Detector

## Leia antes

- codex/realmente.md
- specs/MANIFEST.yaml
- specs/detectors/<path-da-spec>

## Tarefa

Implementar apenas o detector X.

## Restrições

- Não implementar outros detectores.
- Não alterar schemas sem necessidade.
- Não alterar report engine.
- Criar fixtures positivas e negativas.
- Criar testes.

## Critérios de conclusão

- Testes passam.
- Detector registrado.
- Finding segue schema.
- README ou MANIFEST atualizado, se necessário.
```

---

# `codex/realmente.md`

Este arquivo deve ser curto, mas sempre atualizado. Ele é o que você manda o Codex reler depois de compactar contexto.

```md
# Realmente — Estado Canônico do Projeto

## Produto

Estamos criando uma plataforma de auditoria automatizada para contratos Solidity/EVM.

## MVP

CLI local que escaneia arquivos `.sol`, executa detectores estáticos e gera report HTML/PDF.

## Stack

- TypeScript
- Node.js
- @solidity-parser/parser
- Vitest
- Playwright para PDF

## Estrutura de specs

Specs ficam em `/specs`.

Detectores seguem:
`specs/detectors/<domain>/DET-<DOMAIN>-<NUMBER>-<slug>.md`

Schemas humanos ficam em:
`specs/schemas/`

Schemas técnicos ficam em:
`schemas/json/`

## Status de specs

draft → accepted → implemented → verified → deprecated

## Detectores MVP

- DET-COMP-001 Floating Pragma
- DET-COMP-002 Outdated Compiler Version
- DET-SEC-001 Missing Zero Address Validation
- DET-SEC-002 Missing Events
- DET-SEC-003 Unsafe ERC20 Transfer Return Value
- DET-ERC-001 Approve Front-Running
- DET-OWN-001 Hardcoded Address
- DET-DOC-001 Missing NatSpec Comments
- DET-GAS-001 Public Constants Can Be Private
- DET-GAS-002 Storage Variable Caching
- DET-GAS-003 Unused Imports

## Regra para Codex

Nunca implementar uma spec em status `draft`, exceto se o usuário pedir explicitamente.
```

---

# Minha recomendação final

Eu usaria esta convenção como padrão:

```txt
specs/
  detectors/<domain>/DET-<DOMAIN>-<NNN>-<slug>.md
  schemas/SCHEMA-<NNN>-<slug>.md
  reports/REPORT-<NNN>-<slug>.md
  architecture/ARCH-<NNN>-<slug>.md
  workflows/WF-<NNN>-<slug>.md

schemas/
  json/<slug>.schema.json

decisions/
  ADR-<NNN>-<slug>.md
```

Exemplo real:

```txt
specs/detectors/security/DET-SEC-001-missing-zero-address-validation.md
schemas/json/finding.schema.json
decisions/ADR-001-use-typescript.md
```

Esse formato é bom porque é **humano**, **rastreável**, **ordenável**, **fácil para o Codex localizar** e **bom para crescer sem virar bagunça**.

---

### 👤 USUÁRIO *(19:28:51 UTC)*:

esse realmente.md existe mesmo ou é uma tradução ptbr de outro nome de arquivo?

---

### 🤖 ASSISTENTE (ChatGPT) *(19:29:03 UTC)*:

`realmente.md` **não é um arquivo padrão do Codex**. Fui eu que propus esse nome como um arquivo de “estado canônico” em português — algo como “o que realmente importa / estado real do projeto”.

O nome oficial/padrão que o Codex reconhece para instruções persistentes de projeto é **`AGENTS.md`**. A documentação oficial diz que o Codex lê arquivos `AGENTS.md` antes de trabalhar, e o comando `/init` no Codex gera um scaffold de `AGENTS.md` para o projeto. citeturn266773search0 citeturn266773search1

Então eu ajustaria assim:

```txt
evm-auditscan/
  AGENTS.md                 # instruções principais que o Codex deve ler
  codex/
    STATE.md                # estado atual do projeto
    CONTEXT.md              # contexto de produto/domínio
    prompts/
      001-implement-detector.md
```

Eu substituiria `codex/realmente.md` por:

```txt
codex/STATE.md
```

ou, em português:

```txt
codex/ESTADO.md
```

Mas minha recomendação prática é usar nomes em inglês, porque combinam melhor com ferramentas, agentes e convenções de repositório:

```txt
AGENTS.md
codex/STATE.md
codex/CONTEXT.md
codex/NEXT_STEPS.md
```

O papel de cada um:

```txt
AGENTS.md
```

Instruções persistentes para o Codex: arquitetura, regras, como implementar, o que não fazer, padrões de teste, como lidar com specs.

```txt
codex/STATE.md
```

Estado resumido do projeto: o que já foi implementado, o que está em andamento, decisões atuais, próxima tarefa.

```txt
codex/CONTEXT.md
```

Contexto de domínio: o que é a plataforma, inspiração nos reports, taxonomia de severidade, famílias de detectores, visão de produto.

```txt
codex/NEXT_STEPS.md
```

Fila objetiva de próximas tarefas.

Eu colocaria no `AGENTS.md` algo assim:

```md
# Project Instructions for Codex

Before starting any task, read:

- specs/MANIFEST.yaml
- codex/STATE.md
- codex/CONTEXT.md
- codex/NEXT_STEPS.md

Use the specs as the source of truth.

Do not implement features whose specs are in `draft`, unless explicitly requested.

For detector work:
- read the detector spec first;
- implement only the requested detector;
- create positive and negative fixtures;
- create unit tests;
- ensure findings follow `schemas/json/finding.schema.json`;
- update `specs/MANIFEST.yaml` when status changes.

Do not broaden scope without asking.
```

Resumo: **`realmente.md` era uma sugestão minha, não uma convenção real**. Para trabalhar bem com Codex, use **`AGENTS.md`** como arquivo oficial de instruções e um `codex/STATE.md` como nosso “realmente.md” renomeado.

---

### 👤 USUÁRIO *(19:31:20 UTC)*:

Quero que você monte um zip com toda a estrutura do projeto e SPECs que você sugeriu além dos prompts de contexto / estado do codex

---

### 🤖 ASSISTENTE (ChatGPT) *(19:34:46 UTC)*:

Montei o ZIP com a estrutura completa do projeto, SPECs, schemas, prompts e arquivos de contexto/estado para Codex.

Incluí:

- `AGENTS.md`
- `codex/STATE.md`
- `codex/CONTEXT.md`
- `codex/NEXT_STEPS.md`
- `codex/prompts/`
- `specs/MANIFEST.yaml`
- specs de arquitetura, schemas, reports, scoring, workflows, CLI/API
- specs de detectores MVP, v0.2, v0.3 e research
- JSON Schemas em `schemas/json/`
- fixtures Solidity iniciais
- exemplos de report e scan-result
- ADRs e docs auxiliares

Arquivo gerado com **153 arquivos**:

[Baixar o ZIP do projeto/spec kit](sandbox:/mnt/data/evm-auditscan-spec-kit.zip)

---

### 👤 USUÁRIO *(20:49:29 UTC)*:

Fizemos a implementação SDD de outra plataforma com codex e as skills gotalab/cc-sdd , DietrichGebert/ponytail , ghaida/intent. Sua missão agora é reaproveitar parte desse framework de implementação SDD e codificação para nossa aplicação de auditoria solidity EVM

---

### 🤖 ASSISTENTE (ChatGPT) *(20:54:14 UTC)*:

Missão cumprida. Montei um novo pacote adaptando o framework SDD/cc-sdd da outra plataforma para a nossa aplicação de auditoria Solidity/EVM.

Usei o pack anterior como base, mas removi o domínio PrintIntel e adaptei para **EVM AuditScan**: scanner estático, detectores Solidity/EVM, report HTML/PDF, score, fixtures, gates e execução orientada por tasks. Também deixei a camada `.kiro/` compatível com o fluxo `steering → requirements → design → tasks → /kiro-impl`, seguindo o modelo de skills mode do `gotalab/cc-sdd`; o repositório oficial descreve o cc-sdd como um harness SDD com Agent Skills para Codex, Claude Code, Cursor e outros, e a documentação de skill reference menciona o uso de `--codex-skills`. citeturn230505search0turn230505search3

Incluí no ZIP:

- `.kiro/` completo para cc-sdd;
- `AGENTS.md`;
- `CODEX_HANDOFF.md`;
- `CODEX_IMPLEMENTATION_ROADMAP.md`;
- `tasks/TASK-001` até `TASK-012`;
- `testing/` com status, manifest e release scope;
- `scripts/codex-test.sh`;
- `scripts/spec_test_gate.py`;
- `codex/prompts/`;
- `codex/skills/` com skills específicas para detector authoring, report quality, testing gates, arquitetura e security risk;
- docs de compatibilidade cc-sdd;
- specs e schemas do EVM AuditScan preservados;
- fixtures iniciais e exemplos.

Também rodei o gate:

```bash
./scripts/codex-test.sh spec-pack
```

Resultado: **passed**.

O pacote final tem **222 arquivos**.

[Baixar o novo pack SDD/cc-sdd para EVM AuditScan](sandbox:/mnt/data/evm-auditscan-sdd-cc-sdd-codex-pack.zip)

Observação: deixei Ponytail/MCP e intent/design skills como integrações opcionais no guia de skills, sem assumir comandos específicos além do cc-sdd, para evitar acoplar o projeto a detalhes externos que podem variar por instalação.

---

### 👤 USUÁRIO *(21:03:16 UTC)*:

agora, vamos fazer specs para checagem de vulnerabilidades de blockchain / smartcontracts e novos padrões usados em solidity / EVM. Nossa fonte primeira será OWASP, mas caso tenha sugestões, adicione também para termos um backlog de implementações de checagem. Lembre-se de depois revisar o projeto para referenciar as specs novas caso seja necessário

https://owasp.org/www-project-smart-contract-top-10/

---

### 🤖 ASSISTENTE (ChatGPT) *(21:06:57 UTC)*:

Atualizei o pack SDD/cc-sdd com uma nova camada de specs baseada em **OWASP Smart Contract Top 10 2026** e **OWASP SCWE**. A OWASP posiciona o Top 10 como referência para awareness, prevenção e compliance em segurança de smart contracts; a lista 2026 inclui Access Control, Business Logic, Oracle Manipulation, Flash Loans, Input Validation, Unchecked External Calls, Arithmetic Errors, Reentrancy, Integer Overflow/Underflow e Proxy/Upgradeability. citeturn294673view0

Também usei o SCWE como taxonomia de fraquezas para amarrar cada detector a IDs rastreáveis, incluindo itens como Reentrancy, Unchecked Call Return Value, Floating Pragma, Outdated Compiler Version, Missing Slippage Protection, Permit Replay, Storage Layout Collision e ERC4626 Share Inflation. citeturn294673view2

## O que foi adicionado

Incluí **35 novas specs de detectores** cobrindo:

- access control;
- business logic / economic security;
- oracle manipulation;
- flash-loan facilitated attacks;
- input validation;
- unchecked external calls;
- arithmetic / precision / rounding;
- reentrancy variants;
- integer overflow/underflow;
- proxy & upgradeability;
- padrões modernos: **ERC-4626**, **ERC-7201**, **ERC-4337**, **EIP-7702**.

Também adicionei os mapas centrais:

```txt
specs/owasp/OWASP-SC-TOP10-2026-DETECTOR-MAP.md
specs/owasp/OWASP-SCWE-BACKLOG-MAP.md
docs/OWASP_SCS_DETECTOR_BACKLOG.md
```

E revisei/referenciei as novas specs em:

```txt
specs/MANIFEST.yaml
testing/spec-implementation-status.yaml
testing/release-scope.yaml
docs/SPEC_CANONICAL_REFERENCES.md
docs/SPEC_TEST_COVERAGE_MATRIX.md
codex/CONTEXT.md
codex/STATE.md
codex/NEXT_STEPS.md
CODEX_HANDOFF.md
CODEX_IMPLEMENTATION_ROADMAP.md
.kiro/steering/security-risk.md
```

## Novas tasks

Também criei:

```txt
tasks/TASK-013-owasp-scs-backlog-and-schema-metadata.md
tasks/TASK-014-owasp-static-p1-detectors.md
```

A `TASK-013` prepara o schema/report para carregar metadados OWASP.  
A `TASK-014` define a primeira onda de implementação de detectores OWASP estáticos.

## Primeira onda recomendada

Eu deixei como primeira onda prática:

```txt
DET-AUTH-001  Unprotected Privileged Function
DET-INP-001   Missing Bounds Check for Critical Parameters
DET-INP-003   Unvalidated Array Lengths and Loop Bounds
DET-CALL-001  Unchecked Low-Level Call Return
DET-MATH-003  Unsafe Downcast
DET-MATH-005  Pre-0.8 Overflow and Underflow Risk
DET-UPG-004   Missing Disable Initializers
DET-STD-003   Permit Deadline Nonce and Domain Separator Risk
```

Esses são bons porque ainda são relativamente viáveis com AST/heurística estática, antes de entrarmos nos detectores mais semânticos como oracle manipulation, ERC-4626 inflation, read-only reentrancy e flash-loan risk.

## Validação

Rodei o gate:

```bash
./scripts/codex-test.sh spec-pack
```

Resultado: **passed**.

O pack agora tem **137 specs markdown** e **14 tasks**.

[Baixar o pack atualizado com specs OWASP](sandbox:/mnt/data/evm-auditscan-sdd-cc-sdd-codex-pack-owasp.zip)

---

### 👤 USUÁRIO *(21:13:22 UTC)*:

agora, pensamos também em utilizar IA Generativa para realizar as validações e ela entra como um plus nesse processo além das validações herísticas e estáticas. quero que escreva as specs para a criação de validação generativa para cada uma das nossas validações mais relevantes, processo e interface interna (nossa equipe) de curadoria dos prompts, chaves de API e modelos utilizados, integração com forncedores de IA Generativa, etc. Após isso, verifique também as referências de arquitetura, documentação, roadmap e tasks que precisamos atualizar

---

### 🤖 ASSISTENTE (ChatGPT) *(21:17:42 UTC)*:

Feito. Atualizei o pack com uma camada completa de **validação generativa** como complemento das validações estáticas/heurísticas.

Incluí:

- specs `GENAI-001` a `GENAI-009`;
- arquitetura `ARCH-006 — Generative Validation Architecture`;
- workflows `WF-006` e `WF-007`;
- schemas JSON para:
  - `ai-validation-request`;
  - `ai-validation-result`;
  - `prompt-template`;
  - `provider-config`;
- specs para gestão de:
  - providers de IA;
  - chaves/API keys via secret refs;
  - model aliases;
  - prompt registry;
  - curadoria interna de prompts;
  - golden set evaluation;
  - guardrails de custo, dados e rate limit;
- interface interna:
  - `UI-001 — Internal Prompt Curation Console`;
- 16 specs de validadores generativos relevantes:
  - access control;
  - business logic;
  - oracle manipulation;
  - flash loan;
  - input validation;
  - external calls;
  - reentrancy;
  - upgradeability;
  - permit/signature replay;
  - ERC-4626;
  - AMM/slippage/MEV;
  - pair-level cooldown DoS;
  - reflection accounting;
  - hidden owner/special access;
  - arithmetic/precision;
  - report/remediation quality;
- `GENAI-VALIDATOR-DETECTOR-MAP.md`;
- `prompt-registry/` com template inicial;
- nova skill local:
  - `codex/skills/evm-auditscan-genai-validation/SKILL.md`;
- novos prompts Codex:
  - `011-implement-genai-validation-foundation.md`;
  - `012-implement-genai-validator.md`;
- novas tasks:
  - `TASK-015 — GenAI Validation Foundation`;
  - `TASK-016 — Evidence Pack and AI Validation Orchestrator`;
  - `TASK-017 — Prompt Registry and Curation Workflow`;
  - `TASK-018 — Priority GenAI Validators`.

Também revisei e atualizei referências em:

- `AGENTS.md`;
- `CODEX_HANDOFF.md`;
- `CODEX_IMPLEMENTATION_ROADMAP.md`;
- `codex/STATE.md`;
- `codex/CONTEXT.md`;
- `codex/NEXT_STEPS.md`;
- `docs/architecture.md`;
- `docs/roadmap.md`;
- `docs/SPEC_CANONICAL_REFERENCES.md`;
- `docs/SPEC_TEST_COVERAGE_MATRIX.md`;
- `.kiro/specs/evm-auditscan-platform/design.md`;
- `.kiro/specs/evm-auditscan-platform/tasks.md`;
- `.kiro/steering/security-risk.md`;
- `specs/MANIFEST.yaml`;
- `testing/spec-implementation-status.yaml`;
- `testing/release-scope.yaml`;
- `FILE_INDEX.md`;
- `PROJECT_TREE.md`;
- `SPEC_REVIEW_SUMMARY.md`.

A regra central ficou explícita: **IA Generativa é uma camada de validação e enriquecimento, não substitui os detectores determinísticos**. Ela valida evidências, reduz falso positivo, sugere remediação/testes e pode mandar para revisão humana.

Validação executada:

```bash
./scripts/codex-test.sh spec-pack
```

Resultado: **passed**.

O pacote atualizado ficou com **403 arquivos** e **172 specs markdown**.

[Baixar o pack atualizado com validação generativa](sandbox:/mnt/data/evm-auditscan-sdd-cc-sdd-codex-pack-genai.zip)

---

### 👤 USUÁRIO *(21:52:21 UTC)*:

o que está faltando em termos de specs para termos uma visão de plataforma web 100% funcional. Consegue já visualizar a jornada do usuário de ponta a ponta?

---

### 🤖 ASSISTENTE (ChatGPT) *(21:52:50 UTC)*:

Sim. Já dá para visualizar a jornada ponta a ponta, mas o pack atual ainda está mais forte em **engine, detectores, specs OWASP, GenAI e report**, e ainda fraco em **produto web/SaaS completo**.

Hoje temos bem especificado:

- scanner estático local;
- detector engine;
- report engine HTML/PDF;
- scoring;
- OWASP/backlog de detectores;
- validação generativa;
- prompt curation interna;
- fluxo cc-sdd/Codex;
- tasks de implementação do core.

O que ainda falta para uma **plataforma web 100% funcional** é especificar a camada de produto SaaS: autenticação, organizações, projetos, scans assíncronos, dashboard, permissões, billing, API pública, publicação de reports, revisão humana, colaboração, notificações, observabilidade e operação.

# Minha leitura geral

A plataforma pode ter 3 personas principais:

1. **Usuário cliente / builder Web3**  
   Quer escanear um contrato, entender riscos, corrigir e publicar um report.

2. **Time interno / curadoria / segurança**  
   Quer revisar findings, validar prompts de IA, aprovar reports verified e calibrar detectores.

3. **Admin da plataforma**  
   Quer gerenciar usuários, planos, limites, providers, custos, filas, modelos, segurança e incidentes.

Hoje já cobrimos bem a persona 2 em GenAI/prompt curation e a parte técnica da persona 1. Falta detalhar muito da jornada SaaS da persona 1 e quase toda a operação da persona 3.

---

# Jornada ponta a ponta desejada

## 1. Usuário chega na plataforma

Fluxo:

```txt
Landing Page
 → Sign up / Login
 → Criar organização
 → Escolher plano
 → Criar primeiro projeto
```

Specs faltantes:

```txt
WEB-001-public-landing-and-navigation.md
AUTH-001-authentication-and-session-management.md
ORG-001-organization-workspace-model.md
ORG-002-team-invitations.md
BILL-001-plans-quotas-and-subscriptions.md
UX-001-first-run-onboarding.md
```

---

## 2. Usuário cria um projeto

Fluxo:

```txt
Dashboard
 → New Project
 → Nome do projeto
 → Tipo: token, DeFi, NFT, DAO, upgradeable, generic
 → Rede principal
 → Configurações de scan
```

Specs faltantes:

```txt
PROJECT-001-project-lifecycle.md
PROJECT-002-project-metadata.md
PROJECT-003-project-risk-profile.md
SCHEMA-010-project.md
SCHEMA-011-organization.md
SCHEMA-012-user.md
```

Aqui o tipo de projeto é importante porque muda o scan. Um ERC-20 precisa de tokenomics/rug checks; um vault precisa de ERC-4626; um proxy precisa de upgradeability; um protocolo DeFi precisa de oracle/flash-loan/MEV.

---

## 3. Usuário escolhe o alvo do scan

Fluxo:

```txt
New Scan
 → Upload .sol / zip
 → GitHub repo
 → Contract address
 → Paste source code
```

Specs parcialmente existentes: temos CLI/local scan e API inicial de scan.

Specs faltantes para web completa:

```txt
TARGET-001-scan-target-model.md
INGEST-001-upload-source-ingestion.md
INGEST-002-git-repository-ingestion.md
INGEST-003-block-explorer-ingestion.md
INGEST-004-pasted-source-ingestion.md
INGEST-005-source-code-normalization.md
SCHEMA-013-scan-target.md
SCHEMA-014-source-artifact.md
```

Também falta especificar limites:

```txt
PLAN-LIMIT-001-upload-size-and-file-count-limits.md
PLAN-LIMIT-002-scan-frequency-and-concurrency-limits.md
```

---

## 4. Plataforma faz pré-validação

Fluxo:

```txt
Source received
 → Detect framework
 → Detect solc version
 → Resolve imports
 → Compile or partial-parse
 → Build AST
 → Build scan context
 → Show pre-flight status
```

Specs parcialmente existentes: parser, scan pipeline, detector engine.

Specs faltantes:

```txt
PREFLIGHT-001-source-validation.md
PREFLIGHT-002-framework-detection.md
PREFLIGHT-003-solc-version-resolution.md
PREFLIGHT-004-import-resolution.md
PREFLIGHT-005-partial-analysis-mode.md
PREFLIGHT-006-scan-readiness-report.md
```

Esse ponto é crítico para UX. O usuário precisa entender por que um scan falhou: import ausente, versão errada de Solidity, contrato não verificado, explorer rate limit, zip inválido etc.

---

## 5. Usuário configura o scan

Fluxo:

```txt
Select scan profile
 → Static MVP
 → OWASP
 → Token Risk
 → AMM/MEV
 → GenAI validation
 → Report mode
 → Run scan
```

Specs faltantes:

```txt
SCANCFG-001-scan-profiles.md
SCANCFG-002-detector-selection.md
SCANCFG-003-severity-thresholds.md
SCANCFG-004-genai-validation-toggle.md
SCANCFG-005-cost-estimation-before-scan.md
SCANCFG-006-scan-policy-presets.md
```

Exemplo de perfis:

```txt
Quick Static Scan
OWASP Security Scan
ERC20 Token Risk Scan
DeFi / AMM Scan
Upgradeable Contract Scan
Full Scan with GenAI Validation
```

---

## 6. Scan roda de forma assíncrona

Fluxo:

```txt
Run scan
 → Job created
 → Queue
 → Worker
 → Parser
 → Detector engine
 → GenAI validation, se habilitado
 → Scoring
 → Report draft
 → Done / Failed / Partial
```

Specs faltantes:

```txt
JOB-001-async-job-lifecycle.md
JOB-002-scan-queue-and-worker-model.md
JOB-003-job-retry-and-timeout-policy.md
JOB-004-job-cancellation.md
JOB-005-partial-failure-handling.md
JOB-006-scan-artifact-storage.md
JOB-007-scan-logs-and-debug-trace.md
SCHEMA-015-scan-job.md
SCHEMA-016-scan-run.md
SCHEMA-017-scan-artifact.md
```

Estados recomendados:

```txt
created
queued
running
parsing
detecting
validating_with_ai
scoring
generating_report
completed
completed_with_warnings
failed
cancelled
```

---

## 7. Usuário vê dashboard de resultado

Fluxo:

```txt
Scan completed
 → Summary dashboard
 → Security score
 → Threat score
 → Findings by severity
 → Findings by category
 → Top risks
 → Detector coverage
 → Files/contracts analyzed
```

Specs parcialmente existentes: report summary, score, finding schema.

Specs faltantes para web:

```txt
WEB-002-app-shell-and-navigation.md
WEB-003-dashboard-home.md
WEB-004-project-detail-page.md
WEB-005-scan-result-dashboard.md
WEB-006-score-card-and-risk-badges.md
WEB-007-findings-filtering-and-search.md
WEB-008-detector-coverage-view.md
UX-002-empty-error-and-loading-states.md
```

---

## 8. Usuário analisa findings

Fluxo:

```txt
Findings list
 → Filter by severity/category/status
 → Open finding
 → View code snippet
 → See impact
 → See remediation
 → See evidence
 → See AI validation, if any
 → Assign status
```

Specs parcialmente existentes: finding schema, GenAI validation result.

Specs faltantes:

```txt
FINDING-001-finding-list-and-filtering.md
FINDING-002-finding-detail-view.md
FINDING-003-code-snippet-and-source-navigation.md
FINDING-004-finding-status-triage.md
FINDING-005-false-positive-suppression.md
FINDING-006-risk-acceptance-workflow.md
FINDING-007-comments-and-collaboration.md
FINDING-008-finding-deduplication-and-grouping.md
FINDING-009-baseline-and-new-findings.md
SCHEMA-018-finding-comment.md
SCHEMA-019-finding-triage-event.md
SCHEMA-020-finding-suppression.md
```

Esse é um ponto que diferencia produto profissional de “gerador de PDF”. O usuário precisa conseguir trabalhar em cima do resultado.

---

## 9. Usuário usa IA Generativa como validação plus

Fluxo:

```txt
Finding High/Medium
 → Build evidence pack
 → Send to selected model/provider
 → Validate exploitability
 → Suggest remediation
 → Suggest test
 → Mark confidence
 → Human review if needed
```

Specs já existentes cobrem boa parte disso.

O que ainda falta na camada web/produto:

```txt
WEB-009-ai-validation-panel.md
GENAI-010-ai-validation-user-controls.md
GENAI-011-ai-validation-cost-preview.md
GENAI-012-ai-validation-audit-log.md
GENAI-013-ai-disagreement-review-queue.md
```

Para uso interno:

```txt
INTERNAL-001-ai-validation-review-console.md
INTERNAL-002-model-provider-health-dashboard.md
INTERNAL-003-prompt-experiment-results.md
```

---

## 10. Usuário corrige e roda novo scan

Fluxo:

```txt
User fixes code
 → Upload/repo commit changes
 → Re-run scan
 → Compare previous vs current
 → Mark fixed findings
 → Show diff
```

Specs faltantes:

```txt
RESCAN-001-rescan-workflow.md
RESCAN-002-scan-comparison.md
RESCAN-003-proof-of-fix-basics.md
RESCAN-004-regression-detection.md
RESCAN-005-finding-history.md
```

Isso é essencial para virar ferramenta de trabalho contínuo, não apenas um snapshot.

---

## 11. Usuário gera report

Fluxo:

```txt
Generate report
 → Select report type
 → Select included findings
 → Add project metadata
 → Add disclaimer
 → Preview
 → Export PDF/HTML/JSON
```

Specs parcialmente existentes: report HTML/PDF.

Specs faltantes:

```txt
REPORT-007-report-builder.md
REPORT-008-report-customization.md
REPORT-009-report-versioning.md
REPORT-010-report-export-formats.md
REPORT-011-report-branding.md
REPORT-012-report-snapshot-immutability.md
SCHEMA-021-report-version.md
SCHEMA-022-report-export.md
```

---

## 12. Usuário publica report

Fluxo:

```txt
Draft report
 → Publish public URL
 → Choose visibility
 → Self-published or verified
 → Share link
 → Optional PDF download
```

Specs parcialmente existentes: publish workflow e verified report.

Specs faltantes:

```txt
PUB-001-public-report-url.md
PUB-002-report-visibility-and-access-control.md
PUB-003-self-published-report-policy.md
PUB-004-verified-report-request.md
PUB-005-report-revocation-and-supersession.md
PUB-006-public-report-seo-and-metadata.md
PUB-007-public-report-abuse-reporting.md
```

Aqui precisamos tomar cuidado: report público não pode parecer garantia absoluta de segurança.

---

## 13. Fluxo de verified report

Fluxo:

```txt
User requests verification
 → Platform locks scan/report version
 → Internal reviewer queue
 → Reviewer validates High/Medium
 → Reviewer resolves false positives
 → Reviewer adds notes
 → Verified seal
 → Publish verified report
```

Specs parcialmente existentes: verified workflow.

Specs faltantes:

```txt
VERIFY-001-verified-report-lifecycle.md
VERIFY-002-reviewer-assignment.md
VERIFY-003-review-checklist.md
VERIFY-004-reviewer-notes.md
VERIFY-005-verification-seal-policy.md
VERIFY-006-conflict-resolution.md
VERIFY-007-review-sla-and-pricing.md
SCHEMA-023-review-task.md
SCHEMA-024-review-note.md
SCHEMA-025-verification-seal.md
```

---

## 14. Time e permissões

Fluxo:

```txt
Owner creates org
 → Invites members
 → Assigns roles
 → Members run scans
 → Reviewer/admin controls reports
```

Specs faltantes:

```txt
AUTHZ-001-role-based-access-control.md
AUTHZ-002-project-permissions.md
AUTHZ-003-report-permissions.md
AUTHZ-004-api-key-permissions.md
AUTHZ-005-internal-admin-permissions.md
SCHEMA-026-role.md
SCHEMA-027-team-member.md
SCHEMA-028-invitation.md
```

Roles sugeridos:

```txt
Org Owner
Org Admin
Project Admin
Developer
Security Reviewer
Billing Admin
Read-only Viewer
Internal Reviewer
Platform Admin
```

---

## 15. Billing, planos e limites

Fluxo:

```txt
Free user
 → Scan limit reached
 → Upgrade
 → Payment
 → Quota updated
 → Invoices
```

Specs faltantes:

```txt
BILL-001-plans-quotas-and-subscriptions.md
BILL-002-metering-and-usage.md
BILL-003-payment-provider-integration.md
BILL-004-invoices-and-receipts.md
BILL-005-plan-enforcement.md
BILL-006-genai-credit-consumption.md
BILL-007-verified-report-pricing.md
SCHEMA-029-plan.md
SCHEMA-030-subscription.md
SCHEMA-031-usage-meter.md
SCHEMA-032-invoice.md
```

Modelo de cobrança possível:

```txt
Free: 3 scans/mês, sem GenAI, sem PDF público
Pro: scans locais/repo, PDF, histórico
Team: org/team, CI, API, GenAI credits
Business: verified reports, white label, prioridade
```

---

## 16. API pública, webhooks e integrações

Specs existentes ainda são iniciais.

Specs faltantes:

```txt
API-003-projects-api.md
API-004-scan-runs-api.md
API-005-findings-api.md
API-006-reports-api.md
API-007-public-reports-api.md
API-008-team-and-org-api.md
API-009-billing-api.md
API-010-webhooks-api.md
API-011-api-keys.md
API-012-openapi-contract.md
WEBHOOK-001-scan-completed.md
WEBHOOK-002-report-published.md
WEBHOOK-003-finding-threshold-exceeded.md
```

Integrações futuras:

```txt
INT-GITHUB-001-github-repository-connection.md
INT-GITHUB-002-github-pr-check.md
INT-GITHUB-003-github-action-result-upload.md
INT-SLACK-001-slack-notifications.md
INT-DISCORD-001-discord-notifications.md
```

---

## 17. Segurança da própria plataforma

Specs essenciais faltantes:

```txt
PLATSEC-001-tenant-isolation.md
PLATSEC-002-secret-storage-and-rotation.md
PLATSEC-003-api-key-management.md
PLATSEC-004-file-upload-security.md
PLATSEC-005-sandboxed-scan-execution.md
PLATSEC-006-rate-limiting-and-abuse-prevention.md
PLATSEC-007-audit-log.md
PLATSEC-008-data-retention-and-deletion.md
PLATSEC-009-public-report-abuse-controls.md
PLATSEC-010-sensitive-source-code-handling.md
```

Isso é muito importante porque a plataforma vai receber código-fonte de contratos que podem ser privados.

---

## 18. Observabilidade e operação

Specs faltantes:

```txt
OBS-001-application-logging.md
OBS-002-metrics-and-dashboards.md
OBS-003-worker-queue-observability.md
OBS-004-provider-cost-and-latency-monitoring.md
OBS-005-error-tracking.md
OBS-006-health-checks.md
OPS-001-environments.md
OPS-002-deployment-topology.md
OPS-003-database-migrations.md
OPS-004-backup-and-restore.md
OPS-005-incident-response.md
```

---

# Estrutura nova de specs que eu adicionaria

Eu criaria estas novas pastas:

```txt
specs/
  product/
  web/
  auth/
  organizations/
  projects/
  scan-targets/
  ingestion/
  jobs/
  findings/
  reports-publication/
  verification/
  billing/
  notifications/
  integrations/
  platform-security/
  observability/
  operations/
  admin/
```

E os schemas novos:

```txt
specs/schemas/
  SCHEMA-010-user.md
  SCHEMA-011-organization.md
  SCHEMA-012-project.md
  SCHEMA-013-scan-target.md
  SCHEMA-014-source-artifact.md
  SCHEMA-015-scan-job.md
  SCHEMA-016-scan-run.md
  SCHEMA-017-scan-artifact.md
  SCHEMA-018-finding-comment.md
  SCHEMA-019-finding-triage-event.md
  SCHEMA-020-finding-suppression.md
  SCHEMA-021-report-version.md
  SCHEMA-022-report-publication.md
  SCHEMA-023-review-task.md
  SCHEMA-024-review-note.md
  SCHEMA-025-verification-seal.md
  SCHEMA-026-role.md
  SCHEMA-027-team-member.md
  SCHEMA-028-invitation.md
  SCHEMA-029-plan.md
  SCHEMA-030-subscription.md
  SCHEMA-031-usage-meter.md
  SCHEMA-032-api-key.md
  SCHEMA-033-webhook-endpoint.md
  SCHEMA-034-audit-log-event.md
```

---

# Tasks novas necessárias

Eu adicionaria uma nova sequência após a `TASK-018`:

```txt
TASK-019-platform-web-product-gap-specs.md
TASK-020-auth-org-rbac-foundation.md
TASK-021-project-and-scan-target-lifecycle.md
TASK-022-async-scan-job-lifecycle.md
TASK-023-web-dashboard-and-scan-results-ui.md
TASK-024-finding-triage-and-collaboration-ui.md
TASK-025-report-builder-and-public-report-publishing.md
TASK-026-verified-report-review-console.md
TASK-027-billing-plans-quotas-and-metering.md
TASK-028-api-keys-webhooks-and-public-api.md
TASK-029-platform-security-and-tenant-isolation.md
TASK-030-observability-ops-and-deployment.md
TASK-031-e2e-user-journey-test-suite.md
```

---

# Jornada visual resumida

```txt
Visitante
  ↓
Cadastro/Login
  ↓
Criar organização
  ↓
Criar projeto
  ↓
Selecionar alvo do scan
  ↓
Pré-validação do código
  ↓
Configurar perfil do scan
  ↓
Executar scan assíncrono
  ↓
Ver dashboard de resultado
  ↓
Abrir findings e evidências
  ↓
Usar GenAI para validação complementar
  ↓
Triage: Pending / Fixed / False Positive / Risk Accepted
  ↓
Corrigir código e rodar rescan
  ↓
Comparar scans
  ↓
Gerar report
  ↓
Publicar como self-published
  ↓
Opcional: solicitar verified report
  ↓
Compartilhar URL pública/PDF
```

---

# Status honesto

Hoje eu diria que temos:

```txt
Core scanner/specs:             forte
Detector backlog:               forte
OWASP/security backlog:         forte
GenAI validation:               forte
CLI/report MVP:                 bom
Web app journey:                fraco/médio
SaaS/auth/orgs/billing:         fraco
Public report publishing:       médio/fraco
Verified report operations:     médio/fraco
Internal admin platform:        fraco
Observability/deployment:       fraco
End-to-end product tests:       fraco
```

Então a resposta é: **sim, já dá para visualizar a jornada inteira**, mas ela ainda não está suficientemente especificada para Codex implementar uma plataforma web completa sem se perder.

O próximo passo ideal é criar uma nova camada de specs chamada algo como:

```txt
Platform Web SaaS Specification Layer
```

com foco em:

1. personas e jornadas;
2. autenticação/organizações;
3. projetos e scans;
4. job lifecycle;
5. dashboard web;
6. findings triage;
7. report builder/publicação;
8. verified report;
9. billing/quotas;
10. segurança/observabilidade;
11. testes E2E.

Minha recomendação: antes de codar web, escrever `UX-001-end-to-end-user-journey.md` e `WEB-001-information-architecture.md`. Esses dois arquivos viram a âncora para todo o resto.

---

### 👤 USUÁRIO *(22:00:22 UTC)*:

vamos escrever esses arquivos, as specs faltantes, atualizar nosso zip e também revisar internamente tudo aquilo que ficou precisando de ajustes por conta da adição das novas specs

---

### 🤖 ASSISTENTE (ChatGPT) *(22:04:36 UTC)*:

Atualizei o pacote com a nova camada de **specs para plataforma web/SaaS 100% funcional** e revisei as referências internas impactadas.

Incluí principalmente:

- `PRODUCT-001 — Platform Web SaaS Vision`
- `UX-001 — End-to-End User Journey`
- `WEB-001 — Information Architecture`
- `ARCH-007 — Web SaaS Architecture`
- specs para auth, orgs, RBAC, projetos, scan targets, ingestão, preflight, scan config, jobs assíncronos, findings, rescan, report builder, publicação, verified reports, billing, API, webhooks, integrações, platform security, observabilidade, operações e admin console
- schemas `SCHEMA-010` até `SCHEMA-034`
- JSON schemas e exemplos correspondentes
- tasks `TASK-019` até `TASK-031`
- prompts Codex novos:
  - `013-write-platform-web-specs.md`
  - `014-implement-web-saas-foundation.md`
- skill local:
  - `evm-auditscan-web-platform`
- docs novas:
  - `WEB_PLATFORM_SPEC_GAP_REVIEW.md`
  - `WEB_PLATFORM_E2E_JOURNEY.md`

Também revisei e atualizei referências em:

- `AGENTS.md`
- `CODEX_HANDOFF.md`
- `CODEX_IMPLEMENTATION_ROADMAP.md`
- `SPEC_REVIEW_SUMMARY.md`
- `codex/STATE.md`
- `codex/CONTEXT.md`
- `codex/NEXT_STEPS.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/SPEC_CANONICAL_REFERENCES.md`
- `docs/SPEC_TEST_COVERAGE_MATRIX.md`
- `.kiro/specs/evm-auditscan-platform/design.md`
- `.kiro/specs/evm-auditscan-platform/tasks.md`
- `specs/MANIFEST.yaml`
- `testing/spec-implementation-status.yaml`
- `testing/release-scope.yaml`
- `FILE_INDEX.md`
- `PROJECT_TREE.md`

Validação executada:

```bash
./scripts/codex-test.sh spec-pack
```

Resultado: **passed**.

O pack atualizado ficou com **542 arquivos**, **331 specs markdown no gate** e **31 tasks**.

[Baixar o ZIP atualizado com a camada Web/SaaS](sandbox:/mnt/data/evm-auditscan-sdd-cc-sdd-codex-pack-web-platform.zip)

---

### 👤 USUÁRIO *(22:06:11 UTC)*:

e as specs que você recomendou aqui, foram adicionadas?



---

### 🤖 ASSISTENTE (ChatGPT) *(22:09:18 UTC)*:

Sim — **mas não estavam 100% como a lista recomendada**.

Fiz uma checagem direta no ZIP anterior comparando com a lista que você anexou agora. A maior parte tinha sido adicionada, mas encontrei **16 itens que estavam ausentes, renomeados ou com conflito de numeração** em relação à lista original de specs recomendadas. A lista anexada inclui exatamente esses blocos de specs para web/SaaS: landing/onboarding, projetos, targets, preflight, scan config, jobs, dashboard, findings, GenAI, rescan, reports, publicação, verified report, billing, APIs, webhooks, segurança e observabilidade. fileciteturn3file0

Corrigi agora e gerei um novo ZIP revisado.

## O que faltava de verdade

Adicionei specs novas para:

- `WEB-010-public-landing-and-navigation.md`
- `UX-003-first-run-onboarding.md`
- `PLAN-LIMIT-001-upload-size-and-file-count-limits.md`
- `PLAN-LIMIT-002-scan-frequency-and-concurrency-limits.md`
- `GENAI-010-ai-validation-user-controls.md`
- `GENAI-011-ai-validation-cost-preview.md`
- `GENAI-012-ai-validation-audit-log.md`
- `GENAI-013-ai-disagreement-review-queue.md`
- `SCHEMA-035-report-export.md`
- `SCHEMA-036-invoice.md`

Também adicionei um documento de auditoria interna:

```txt
docs/WEB_PLATFORM_SPEC_COVERAGE_AUDIT.md
```

Ele registra quais specs estavam presentes, quais foram adicionadas e quais tiveram nome/ID canônico diferente para evitar duplicidade.

## O que estava presente, mas com nome diferente

Algumas specs não estavam com o nome exato da lista porque já havia IDs ocupados. Em vez de criar IDs duplicados, mantive a rastreabilidade com nomes canônicos:

| Recomendação original | Spec canônica no pack |
|---|---|
| `WEB-001-public-landing-and-navigation.md` | `WEB-010-public-landing-and-navigation.md` |
| `UX-001-first-run-onboarding.md` | `UX-003-first-run-onboarding.md` |
| `SCHEMA-010-project.md` | `SCHEMA-012-project.md` |
| `SCHEMA-012-user.md` | `SCHEMA-010-user.md` |
| `SCHEMA-022-report-export.md` | `SCHEMA-035-report-export.md` |
| `SCHEMA-032-invoice.md` | `SCHEMA-036-invoice.md` |
| `API-008-team-and-org-api.md` | `API-008-team-and-organization-api.md` |
| `WEBHOOK-001-scan-completed.md` | `WEBHOOK-001-scan-completed-webhook.md` |
| `WEBHOOK-002-report-published.md` | `WEBHOOK-002-report-published-webhook.md` |
| `WEBHOOK-003-finding-threshold-exceeded.md` | `WEBHOOK-003-finding-threshold-exceeded-webhook.md` |

A decisão correta aqui foi **não criar IDs duplicados**. Por exemplo, `SCHEMA-032` já estava usado para `api-key`, então `invoice` entrou como `SCHEMA-036`.

## Validação

Rodei novamente o gate:

```bash
bash ./scripts/codex-test.sh spec-pack
```

Resultado: **passed**.

O pack revisado agora tem **341 markdown specs** no gate.

[Baixar ZIP revisado v2](sandbox:/mnt/data/evm-auditscan-sdd-cc-sdd-codex-pack-web-platform-v2.zip)

---

### 👤 USUÁRIO *(22:51:19 UTC)*:

Agora, precisamos de spec que garantam que nossa plataforma esteja livre de vulnerabilidades como as da captura de tela e das mais comuns da owasp, sempre prezando pela qualidade de código, software, confidencialidade dos dados e dos nossos serviços. Atualize nosso zip, revise specs do projeto se necessário

---

### 🤖 ASSISTENTE (ChatGPT) *(22:54:58 UTC)*:

Atualizei o pacote com uma camada nova de **Platform Security Baseline**, focada exatamente nas vulnerabilidades da captura e nas famílias mais comuns de OWASP Web/API.

A base ficou alinhada com OWASP Top 10, OWASP API Security Top 10 e ASVS: OWASP trata o Top 10 como documento de referência para riscos críticos de aplicações web; o API Security Top 10 destaca BOLA/IDOR como risco central em APIs; e o ASVS serve como base de requisitos verificáveis de segurança de aplicação. citeturn612133search6turn612133search2turn612133search3

## O que foi adicionado

Criei as specs `PLATSEC-011` até `PLATSEC-026`:

- `PLATSEC-011` — rate limit, brute force e credential stuffing
- `PLATSEC-012` — CORS com allowlist, sem refletir `Origin`
- `PLATSEC-013` — minimização de resposta e bloqueio de vazamento de PII/secrets
- `PLATSEC-014` — JWT fora da URL, logout com revogação e lifecycle de sessão
- `PLATSEC-015` — proteção contra enumeração de usuário
- `PLATSEC-016` — clickjacking e security headers
- `PLATSEC-017` — proteção contra SQL Injection
- `PLATSEC-018` — IDOR/BOLA e object-level authorization
- `PLATSEC-019` — CSRF em ações autenticadas por cookie
- `PLATSEC-020` — XSS, CSP e output encoding
- `PLATSEC-021` — classificação, retenção e redaction de dados sensíveis
- `PLATSEC-022` — tratamento seguro de erros
- `PLATSEC-023` — segurança de dependências e supply chain
- `PLATSEC-024` — SAST, DAST, secret scanning e gates de segurança
- `PLATSEC-025` — processamento seguro de uploads de código-fonte
- `PLATSEC-026` — suíte de regressão de segurança da plataforma

Também adicionei:

- `ARCH-008 — Platform Security Architecture`
- `WF-008 — Platform Security Review Workflow`
- `GATE-001 — Platform Security CI Gate`
- `SCHEMA-037 — Security Control`
- `SCHEMA-038 — Security Gate Result`
- JSON Schemas e exemplos correspondentes
- docs:
  - `docs/PLATFORM_SECURITY_BASELINE.md`
  - `docs/OWASP_WEB_API_SECURITY_MAPPING.md`
  - `docs/SECURITY_SPEC_COVERAGE_AUDIT.md`
- tasks:
  - `TASK-032` até `TASK-036`

Essas specs cobrem diretamente os itens da captura: rate limit ausente, CORS permissivo, excesso de dados/PII na resposta, JWT em URL, token válido após logout, enumeração de usuário, clickjacking, SQL Injection e IDOR/BOLA. OWASP também documenta controles relevantes para headers de segurança, SQL Injection e exposição excessiva de propriedades em APIs. citeturn612133search5turn612133search13turn612133search7

## Revisões internas feitas

Atualizei as referências em:

- `AGENTS.md`
- `CODEX_HANDOFF.md`
- `CODEX_IMPLEMENTATION_ROADMAP.md`
- `codex/STATE.md`
- `codex/CONTEXT.md`
- `codex/NEXT_STEPS.md`
- `.kiro/steering/security-risk.md`
- `.kiro/specs/evm-auditscan-platform/design.md`
- `.kiro/specs/evm-auditscan-platform/tasks.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/SPEC_CANONICAL_REFERENCES.md`
- `docs/SPEC_TEST_COVERAGE_MATRIX.md`
- `specs/MANIFEST.yaml`
- `testing/spec-implementation-status.yaml`
- `testing/release-scope.yaml`
- `FILE_INDEX.md`
- `PROJECT_TREE.md`
- `SPEC_REVIEW_SUMMARY.md`

## Validação

Rodei o gate:

```bash
bash ./scripts/codex-test.sh spec-pack
```

Resultado: **passed**.

O pack agora está com:

- **362 specs markdown**
- **36 tasks**
- **702 arquivos no ZIP**

[Baixar ZIP atualizado com Platform Security Baseline](sandbox:/mnt/data/evm-auditscan-sdd-cc-sdd-codex-pack-platform-security.zip)

---

### 👤 USUÁRIO *(23:06:33 UTC)*:

Agora, na parte de monetização a ideia é termos opções de pagamento através de cryptoativos como diferencial também. Queremos receber por enquanto através de um intermediário de pagamento com crypto, mas no futuro, faremos nossa própria implementação para recebimento em nossas carteiras. Faça casos de uso para recebimento nas redes mais comuns de cryptoativos através de algum intermediário conhecido e escreva as spec necessárias para a jornada de pagamento por relatório. Atualize nosso zip e revise os arquivos do projeto que precisem de alteração por conta dessa mudança na jornada de pagamento 

---

### 🤖 ASSISTENTE (ChatGPT) *(23:10:47 UTC)*:

Atualizei o pacote com a camada de **monetização por pagamento em cryptoativos por relatório**, mantendo a regra arquitetural que você pediu: **no MVP usamos intermediários de pagamento; recebimento direto em carteiras próprias fica preparado, mas como evolução futura**.

Usei como base providers conhecidos e documentei casos de uso para **BitPay**, **NOWPayments**, **CoinPayments** e **Coinbase Business/Payments**. BitPay trabalha com fluxo de invoices e checkout/modal; NOWPayments oferece API, invoices e suporte amplo a moedas; CoinPayments documenta API REST, webhooks e endpoint de currencies; Coinbase vem migrando o foco para Coinbase Business/Payments e stablecoin payments, com stack voltada a USDC/Base. citeturn612036search2turn612036search14turn612036search21turn612036search11turn612036search18

## O que foi adicionado

Incluí specs `PAY-001` até `PAY-017`, cobrindo:

- jornada de pagamento crypto por relatório;
- abstração de provider;
- configuração de intermediários;
- payment intent;
- quote com expiração;
- hosted invoice checkout;
- webhooks verificados;
- idempotência;
- state machine de pagamento;
- desbloqueio de report entitlement;
- underpayment, overpayment, expiração e refunds;
- fees, FX e price expiry;
- ledger e reconciliação;
- failover/manual review;
- compliance e termos;
- política de redes/ativos suportados;
- boundary de custódia/settlement;
- segurança de secrets e webhooks;
- recebimento direto em carteiras próprias como arquitetura futura.

Também adicionei casos de uso `UC-PAY-001` até `UC-PAY-005`:

- pagar relatório via **BitPay hosted invoice**;
- pagar relatório via **NOWPayments multi-asset invoice**;
- pagar relatório via **CoinPayments currency route**;
- pagar relatório via **Coinbase stablecoin payments**;
- revisão manual e reconciliação de pagamentos problemáticos.

A spec de redes/ativos cobre backlog para BTC, Ethereum, Base, Arbitrum, Optimism, Polygon, BNB Smart Chain, Tron, Solana, stablecoins como USDC/USDT e redes opcionais suportadas por providers. A regra é não hardcodar: a lista final vem da interseção entre **provider support + allowlist interna + risco/compliance + UX/custo**.

## Arquivos novos principais

Adicionados:

```txt
specs/payments/PAY-001..PAY-017
specs/use-cases/payments/UC-PAY-001..UC-PAY-005
specs/architecture/ARCH-009-crypto-payment-architecture.md
specs/workflows/WF-009-pay-per-report-crypto-payment-workflow.md
specs/api/API-013-payments-api.md
specs/api/API-014-crypto-payment-provider-webhooks-api.md
specs/billing/BILL-008-crypto-pay-per-report-pricing-and-entitlements.md
specs/billing/BILL-009-crypto-payment-reconciliation-and-ledger.md
specs/security-gates/GATE-002-crypto-payment-security-and-reconciliation-gate.md
specs/schemas/SCHEMA-039..SCHEMA-046
```

Também adicionei JSON schemas e exemplos para:

```txt
payment-provider-config
payment-intent
payment-quote
crypto-payment-invoice
payment-webhook-event
wallet-settlement
payment-ledger-entry
report-entitlement
```

## Jornada especificada

A jornada ficou assim:

```txt
Usuário quer exportar/publicar relatório pago
  → escolhe pagar com crypto
  → plataforma cria PaymentIntent
  → plataforma cria PaymentQuote
  → provider cria hosted invoice/checkout
  → usuário paga na rede/asset escolhido
  → provider envia webhook
  → plataforma valida assinatura/idempotência
  → payment status vira confirmed/settled
  → ledger é atualizado
  → ReportEntitlement é liberado
  → usuário pode baixar/publicar o relatório
```

Regra crítica: **redirect de checkout nunca libera relatório sozinho**. O acesso pago depende de webhook verificado ou reconciliação equivalente.

## Segurança e qualidade

Incluí um gate específico:

```txt
GATE-002 — Crypto Payment Security and Reconciliation Gate
```

Ele exige testes para:

- assinatura inválida de webhook;
- replay de webhook;
- evento duplicado/idempotência;
- IDOR em payment intent/status;
- token/JWT fora de URL;
- ausência de secrets em logs;
- relatório bloqueado antes do pagamento confirmado;
- underpayment sem desbloqueio automático.

Também revisei as referências em:

- `AGENTS.md`
- `CODEX_HANDOFF.md`
- `CODEX_IMPLEMENTATION_ROADMAP.md`
- `SPEC_REVIEW_SUMMARY.md`
- `codex/STATE.md`
- `codex/CONTEXT.md`
- `codex/NEXT_STEPS.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/SPEC_CANONICAL_REFERENCES.md`
- `docs/SPEC_TEST_COVERAGE_MATRIX.md`
- `.kiro/specs/evm-auditscan-platform/design.md`
- `.kiro/specs/evm-auditscan-platform/tasks.md`
- `.kiro/steering/security-risk.md`
- `specs/MANIFEST.yaml`
- `testing/spec-implementation-status.yaml`
- `testing/release-scope.yaml`
- `FILE_INDEX.md`
- `PROJECT_TREE.md`

## Novas tasks

Adicionei:

```txt
TASK-037 — Crypto payment spec layer
TASK-038 — Crypto provider abstraction and sandbox
TASK-039 — Pay-per-report checkout and entitlement
TASK-040 — Payment webhooks reconciliation and ledger
TASK-041 — Future direct wallet receipt research
```

Também incluí prompt e skill local para Codex:

```txt
codex/prompts/015-implement-crypto-payment-provider-abstraction.md
codex/skills/evm-auditscan-crypto-payments/SKILL.md
```

## Validação

Rodei o gate:

```bash
bash ./scripts/codex-test.sh spec-pack
```

Resultado: **passed**.

Resumo do pack:

- **399 specs markdown**
- **41 tasks**
- **10 skills locais**
- **652 arquivos no ZIP**

[Baixar ZIP atualizado com crypto payments](sandbox:/mnt/data/evm-auditscan-sdd-cc-sdd-codex-pack-crypto-payments.zip)

---

### 👤 USUÁRIO *(23:16:52 UTC)*:

Agora quero também uma jornada de pagamento com cartão de crédito. Mais uma vez, usaremos um intermediário conhecido para fazermos a transação. Atualize nossas specs para essa jornada e também revise nosso zip pra ver se não existem outros pontos que precisem de modificações por conta dessas novas adições 

---

### 👤 USUÁRIO *(23:19:04 UTC)*:

Agora quero também uma jornada de pagamento com cartão de crédito. Mais uma vez, usaremos um intermediário conhecido para fazermos a transação. Lembre-se que apesar de eu ser Brasileiro, nossos clientes provavelmente serão de outros países, portante verifiquem se eles conseguirão me pagar utilizando a opção de intermediário de pagamento escolhido. Atualize nossas specs para essa jornada e também revise nosso zip pra ver se não existem outros pontos que precisem de modificações por conta dessas novas adições 

---

### 🤖 ASSISTENTE (ChatGPT) *(23:22:50 UTC)*:

Sim — atualizei o ZIP com a jornada de **pagamento por cartão de crédito/débito para pagamento avulso por relatório**.

Escolhi **Stripe Checkout como intermediário primário** e **PayPal como fallback/alternativa**. A escolha faz sentido porque a Stripe informa que, se o país da empresa é suportado, é possível vender para clientes em qualquer lugar do mundo; no Brasil, a Stripe documenta suporte a cartões Visa/Mastercard, Apple Pay/Google Pay e débito internacional não brasileiro, além de tarifas específicas para cartões internacionais. citeturn458801search2turn458801search0turn458801search25 O PayPal entra como fallback porque a página empresarial brasileira informa aceitação de cartões de crédito/débito e pagamentos globais. citeturn458801search12turn458801search4

A ressalva importante é: isso **não garante aprovação automática da conta merchant** nem disponibilidade de todas as bandeiras/países em produção. A spec deixa claro que a UI não deve prometer bandeiras ou métodos não suportados regionalmente, e que a habilitação final depende do onboarding, análise de risco e configuração do provider.

## O que foi adicionado

Incluí specs novas para:

- `ARCH-010` — arquitetura de pagamento por cartão;
- `WF-010` — workflow de pagamento por relatório com cartão;
- `API-015` — Card Payments API;
- `API-016` — Card Provider Webhooks API;
- `BILL-010` — precificação e entitlement por cartão;
- `GATE-003` — gate de segurança para cartão/entitlement;
- `PAY-018` até `PAY-029` — jornada, Stripe Checkout, fallback PayPal, webhooks, 3DS/SCA, retry, refunds, disputes, PCI boundary, roteamento cartão/crypto;
- `UC-PAY-006` até `UC-PAY-010` — casos de uso para cartão internacional, cliente BR, falha/3DS, refund/dispute e fallback PayPal;
- `SCHEMA-047` até `SCHEMA-054` — schemas de provider config, checkout session, card payment intent, webhook event, refund, dispute, routing policy e entitlement reversal.

Também adicionei:

- `docs/CARD_PAYMENT_JOURNEY.md`
- `docs/CARD_PAYMENT_PROVIDER_REVIEW.md`
- `codex/skills/evm-auditscan-card-payments/SKILL.md`
- `codex/prompts/016-implement-card-payment-provider-abstraction.md`
- tasks `TASK-042` até `TASK-046`.

## Regra central da jornada

A spec ficou com esta regra de segurança:

```txt
Report bloqueado
  → usuário escolhe pagar com cartão
  → backend cria PaymentIntent
  → provider cria hosted checkout
  → usuário paga no ambiente do provider
  → provider envia webhook assinado
  → plataforma valida webhook e idempotência
  → ledger é atualizado
  → ReportEntitlement é liberado
```

O **redirect de sucesso do checkout nunca libera o relatório sozinho**. O relatório só é liberado após webhook verificado ou reconciliação equivalente.

## Revisões internas feitas

Atualizei referências em:

- `AGENTS.md`
- `CODEX_HANDOFF.md`
- `CODEX_IMPLEMENTATION_ROADMAP.md`
- `SPEC_REVIEW_SUMMARY.md`
- `codex/STATE.md`
- `codex/CONTEXT.md`
- `codex/NEXT_STEPS.md`
- `.kiro/specs/evm-auditscan-platform/design.md`
- `.kiro/specs/evm-auditscan-platform/tasks.md`
- `.kiro/steering/security-risk.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/SPEC_CANONICAL_REFERENCES.md`
- `docs/SPEC_TEST_COVERAGE_MATRIX.md`
- `specs/MANIFEST.yaml`
- `testing/spec-implementation-status.yaml`
- `testing/release-scope.yaml`
- `FILE_INDEX.md`
- `PROJECT_TREE.md`

## Validação

Rodei o gate:

```bash
bash ./scripts/codex-test.sh spec-pack
```

Resultado: **passed**.

Resumo do pacote:

- **430 specs markdown**
- **46 tasks**
- **11 skills locais**
- **708 arquivos no ZIP**

[Baixar ZIP atualizado com pagamento por cartão](sandbox:/mnt/data/evm-auditscan-sdd-cc-sdd-codex-pack-card-payments.zip)

---

### 👤 USUÁRIO *(23:30:58 UTC)*:

Agora, contratos inteligentes muitas vezes fazem referência a outros contratos que precisarão ser auditados. Quero agora que você, dentro da parte de monetização, entre com alguns modelos de proposição para a cobrança do relatório. No solidityscan.com eles cobram por linha de código auditada dentro de alguns planos de assinatura, mas aqui queremos ser mais cirúrgicos e cobrar por relatório e dimensionar o preço de acordo com a complexidade do contrato 

---

### 🤖 ASSISTENTE (ChatGPT) *(23:34:16 UTC)*:

Atualizei o pacote com uma nova camada de **precificação por complexidade e escopo auditável**, cobrindo exatamente o ponto dos contratos referenciados.

Agora a monetização por relatório não fica presa a “linhas de código auditadas”. O modelo especificado considera:

- contrato principal;
- contratos herdados/importados;
- libraries customizadas;
- proxies e implementations;
- contratos externos críticos;
- oracles;
- routers/pairs/factories de DEX;
- vaults, strategies e adapters;
- delegatecall;
- upgradeability;
- tokenomics;
- quantidade de funções públicas/externas;
- chamadas externas;
- nível de validação: estática, OWASP, token risk, AMM/MEV, GenAI, verified review.

## O que foi adicionado

Incluí novas specs:

```txt
ARCH-011  Report Pricing and Contract Scope Architecture
WF-011    Report Complexity Pricing Workflow
API-017   Pricing Quotes API

PRICING-001  Report Complexity Pricing Model
PRICING-002  Contract Scope Discovery and Referenced Contracts
PRICING-003  Complexity Estimation Engine
PRICING-004  Report Scope Lock and Quote Approval
PRICING-005  Dependency Graph and Audit Scope Boundary
PRICING-006  Complexity Tier Policy
PRICING-007  Price Adjustment Rescan and Additional Scope Policy

BILL-011  Report Complexity Pricing and Entitlements
BILL-012  Referenced Contract Scope Pricing
```

Também adicionei schemas novos:

```txt
SCHEMA-055  Report Pricing Quote
SCHEMA-056  Contract Scope Node
SCHEMA-057  Contract Dependency Graph
SCHEMA-058  Complexity Assessment
SCHEMA-059  Report Scope
SCHEMA-060  Pricing Policy
```

E casos de uso:

```txt
UC-PAY-011  Simple Contract Report with Lite Pricing
UC-PAY-012  Token Contract with Referenced Contracts
UC-PAY-013  DeFi Protocol Multi Contract Scope
UC-PAY-014  User Approves Expanded Scope After Preflight
UC-PAY-015  Incomplete Scope Quoted as Partial Report
```

## Modelo de cobrança especificado

A proposta principal ficou assim:

```txt
Report price =
  base_report_price
  × complexity_multiplier
  × scope_multiplier
  × validation_depth_multiplier
  + optional_verified_review_fee
```

Com tiers:

```txt
Lite       → contrato simples, baixo acoplamento
Standard   → token/app com dependências moderadas
Advanced   → DeFi, tokenomics, proxy, oracle, AMM, múltiplos contratos
Protocol   → sistema multi-contrato com vaults, strategies, governance
Enterprise → escopo manual, verified review, SLA, multi-chain
```

A regra principal agora é:

> **A plataforma deve gerar um `ReportScope` e um `ReportPricingQuote` antes do pagamento. O pagamento só libera o relatório para aquele escopo congelado.**

## Como entram contratos referenciados

Adicionei classificação explícita:

```txt
primary              → contrato principal do relatório
included_dependency  → contrato incluído na auditoria e no preço
trusted_reference    → dependência conhecida/oficial, apenas referenciada
external_critical    → contrato externo crítico para segurança
unverified_external  → dependência externa sem source verificado
excluded             → fora do escopo, com disclaimer
```

Exemplos de regra:

- OpenZeppelin oficial não modificado: `trusted_reference`
- fork local de OpenZeppelin: `included_dependency`
- proxy implementation: `included_dependency`
- oracle customizado: `included_dependency` ou `external_critical`
- Uniswap router oficial: `trusted_reference` + validação de integração
- strategy/vault customizado: `included_dependency`
- contrato externo crítico não verificado: exige disclaimer, revisão manual ou quote complementar

## Integração com cartão e crypto

A camada de pagamento agora consome o preço final de `ReportPricingQuote`.

Ou seja:

```txt
ComplexityAssessment
 → ReportScope
 → ReportPricingQuote
 → PaymentIntent cartão/crypto
 → webhook confirmado
 → ReportEntitlement
```

O provider de pagamento não calcula o preço. Ele só recebe o valor final já aprovado.

## Novas tasks

Adicionei:

```txt
TASK-047  Report Complexity Pricing Spec Layer
TASK-048  Contract Scope Graph and Complexity Estimator
TASK-049  Pricing Quote Payment Entitlement Integration
TASK-050  Multi Contract Report Scope UI and Disclosure
```

Também adicionei:

```txt
codex/prompts/017-implement-report-complexity-pricing.md
codex/skills/evm-auditscan-pricing-scope/SKILL.md
docs/REPORT_COMPLEXITY_PRICING_MODELS.md
docs/CONTRACT_SCOPE_AND_REFERENCED_CONTRACTS.md
```

## Revisões internas

Atualizei referências em:

- `AGENTS.md`
- `CODEX_HANDOFF.md`
- `CODEX_IMPLEMENTATION_ROADMAP.md`
- `codex/STATE.md`
- `codex/CONTEXT.md`
- `codex/NEXT_STEPS.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/SPEC_CANONICAL_REFERENCES.md`
- `docs/SPEC_TEST_COVERAGE_MATRIX.md`
- `.kiro/specs/evm-auditscan-platform/design.md`
- `.kiro/specs/evm-auditscan-platform/tasks.md`
- `.kiro/steering/security-risk.md`
- `specs/MANIFEST.yaml`
- `testing/spec-implementation-status.yaml`
- `testing/release-scope.yaml`
- `FILE_INDEX.md`
- `PROJECT_TREE.md`
- `SPEC_REVIEW_SUMMARY.md`

## Validação

Rodei:

```bash
bash ./scripts/codex-test.sh spec-pack
```

Resultado: **passed**.

Resumo do pacote:

- **453 specs markdown**
- **50 tasks**
- **12 skills locais**
- **872 arquivos no ZIP**

[Baixar ZIP atualizado com precificação por complexidade](sandbox:/mnt/data/evm-auditscan-sdd-cc-sdd-codex-pack-complexity-pricing.zip)

---
