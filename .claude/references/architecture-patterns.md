# Architecture Patterns for AI Coding: Why Your File Structure Matters More Than Your Prompts

**By Rasmus Widing**
_Product Builder | AI Adoption Specialist | Creator of the PRP Framework_

In [Part 1](link-to-article-1), I showed you how to set up tooling. Now let's talk about something more controversial: why your architecture might be working against you.

After three years of building software with AI coding tools and working with engineering teams on AI adoption, I've discovered something counterintuitive: **The architecture pattern you choose has more impact on AI productivity than the prompts you write**.

Most developers focus on crafting better prompts or switching between AI tools for the new flavor of the week. But I've watched engineering teams with the same AI coding assistant—one team producing 10× more output than another. One major differentiator is the architecture pattern they use.

In this article, I'll break down the architectural patterns that work (and don't work) with AI coding agents, backed by research from Anthropic and my own experience building the PRP framework.

## The Hidden Cost of Traditional Architecture

Here's the problem most teams don't realize they have: **Traditional layered architecture burns tokens like crazy—it's like running a diesel generator to charge your Tesla**.

When an AI agent needs to understand how adding a product to the catalog works in a traditional layered architecture, it has to traverse:

```
controllers/product_controller.py     # 1. Entry point
services/product_service.py           # 2. Business logic
repositories/product_repository.py    # 3. Data access
models/product.py                     # 4. Data model
validators/product_validator.py       # 5. Validation rules
dto/product_dto.py                   # 6. Data transfer objects
```

That's **six files** across **six different directories** just to understand one feature. Each context switch costs tokens. Each file requires loading into the AI's context window. The agent spends 60-70% of its time just navigating your architecture.

Compare this to modern AI-friendly approaches where everything for a feature lives together. The difference is dramatic—and measurable.

## The Architecture Patterns: A Comparative Analysis

I've evaluated the major architectural patterns based on four critical dimensions for AI coding:

| Pattern                                  | AI-Friendliness | Token Efficiency | Maintainability | Complexity |
| ---------------------------------------- | --------------- | ---------------- | --------------- | ---------- |
| **Vertical Slice Architecture**          | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐⭐       | ⭐⭐⭐⭐        | ⭐⭐       |
| **Feature Folders / Package by Feature** | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐         | ⭐⭐⭐⭐        | ⭐⭐       |
| **Modular Monolith**                     | ⭐⭐⭐⭐        | ⭐⭐⭐⭐         | ⭐⭐⭐⭐        | ⭐⭐⭐     |
| **Clean/Layered Architecture**           | ⭐⭐⭐          | ⭐⭐             | ⭐⭐⭐⭐⭐      | ⭐⭐⭐     |
| **Microservices**                        | ⭐⭐            | ⭐⭐             | ⭐⭐⭐          | ⭐⭐⭐⭐⭐ |
| **Single File / Monolith**               | ⭐⭐            | ⭐⭐⭐⭐⭐       | ⭐              | ⭐         |

**Rating Definitions:**

- **AI-Friendliness**: How easily can an AI agent understand and modify code?
- **Token Efficiency**: How many tokens are consumed for typical operations?
- **Maintainability**: How easy is it for humans to maintain long-term?
- **Complexity**: How much overhead to implement and operate? (Lower stars = less complex)

Let's break down each pattern.

## Pattern 1: Vertical Slice Architecture (The Winner)

**What it is:** Organize code by feature (vertical slices) rather than by technical layer (horizontal layers). Each slice contains everything needed for that feature—routes, business logic, data access, tests.

**Structure:**

```
app/
├── products/
│   ├── routes.py           # FastAPI endpoints
│   ├── service.py          # Business logic
│   ├── repository.py       # Database access
│   ├── types.py            # Models, DTOs, schemas
│   ├── validators.py       # Input validation
│   ├── test_routes.py      # Endpoint tests
│   ├── test_service.py     # Business logic tests
│   └── README.md           # Feature documentation
├── inventory/
│   ├── routes.py
│   ├── service.py
│   ├── types.py
│   └── ...
└── categories/
    └── ...
```

**Why it wins for AI coding:**

1. **Context isolation** - AI agent only needs to understand one feature directory
2. **Token efficiency** - All related code is co-located, no cross-directory navigation
3. **High cohesion** - Everything needed for adding products lives in `products/`
4. **Grep-ability** - Search for "product" finds all product-related code in one place
5. **Parallel development** - Different agents (or devs) can work on different features simultaneously without conflicts

**Real-world impact:**

A team I advised switched from layered to vertical slice architecture. Their AI coding agent's productivity increased by 3×. Not because the agent got smarter—because it stopped wasting tokens navigating between layers.

As one developer on the Cursor AI team noted: "VSA provides context isolation—AI tools can more easily understand and modify self-contained features without requiring extensive knowledge of the entire codebase."

**Trade-offs:**

- Some code duplication across slices (but duplication is cheaper than coupling with AI)
- Requires discipline to maintain slice boundaries
- Shared infrastructure (auth, logging, database) lives in `common/` or `shared/`

**When to use:** Building new applications, refactoring medium-to-large applications, working extensively with AI agents.

## Pattern 2: Feature Folders / Package by Feature

**What it is:** Similar to Vertical Slice, but typically less strict. Organizes by feature but may share more infrastructure code.

**Structure:**

```
app/
├── features/
│   ├── product_catalog/
│   │   ├── api.py
│   │   ├── models.py
│   │   ├── business_logic.py
│   │   └── tests.py
│   └── inventory_management/
│       └── ...
├── shared/
│   ├── database.py
│   ├── auth.py
│   └── ...
```

**Why it works for AI coding:**

- **High cohesion within features** - Related code lives together
- **Reduced navigation** - AI agent stays within feature boundaries
- **Natural boundaries** - Clear where code belongs
- **Easy to extract to microservices later** if needed

**Trade-offs:**

- Less prescriptive than VSA
- Can lead to "junk drawer" shared folders
- Boundaries between features and shared code sometimes unclear

**When to use:** Teams transitioning from layered architecture, projects with significant shared infrastructure, teams new to AI coding.

## Pattern 3: Modular Monolith

**What it is:** Single deployable unit organized into loosely coupled modules with explicit interfaces between them.

**Structure:**

```
app/
├── modules/
│   ├── products/
│   │   ├── domain/         # Business logic
│   │   ├── application/    # Use cases
│   │   ├── infrastructure/ # DB, external APIs
│   │   └── interface/      # HTTP, CLI
│   ├── inventory/
│   └── ...
```

**Why it works for AI coding:**

- **Clear module boundaries** - AI agent knows which module to work in
- **Explicit interfaces** - Dependencies between modules are clear
- **Good for larger codebases** - Scales better than flat structure
- **Single deployment** - Simpler than microservices

**Trade-offs:**

- More complex than VSA or feature folders
- Still requires navigation within modules (domain → application → infrastructure)
- Harder for AI to understand module dependencies

**When to use:** Large applications (>50K lines), teams with strong architectural discipline, need for strict module boundaries.

## Pattern 4: Clean/Layered Architecture

**What it is:** Traditional horizontal layers—controllers, services, repositories, models. The "MVC" or "N-tier" approach most developers learned.

**Structure:**

```
app/
├── controllers/     # HTTP handlers
├── services/        # Business logic
├── repositories/    # Data access
├── models/          # Data models
└── dto/            # Data transfer objects
```

**Why it struggles with AI coding:**

- **Low cohesion** - Product-related code scattered across five directories
- **High navigation cost** - AI must traverse layers to understand one feature
- **Token inefficiency** - Loading six files to understand adding a product
- **Context switching** - AI loses track of purpose while navigating

**When it still makes sense:**

Yes, layered architecture works for small apps under 5K lines. So does Excel. Neither is what you should reach for in 2025.

**The harsh truth:** Clean Architecture was designed for human maintainability at scale. But AI agents don't think in layers—they think in features. In 2025, when AI agents increasingly drive development, building layered architectures is like optimizing for horses when everyone's driving cars. Fighting your architecture costs you productivity every single day.

## Pattern 5: Microservices

**What it is:** Multiple independent services, each deployed separately, communicating over network.

**Why it's challenging for AI coding:**

- **Context fragmentation** - AI agent needs to understand multiple repositories
- **Coordination overhead** - Changes often span multiple services
- **State management complexity** - Conversation context split across services
- **Testing complexity** - Integration tests require multiple services running
- **Network boundaries** - AI can't easily traverse service calls

**The microservices paradox:** While microservices architecture divides concerns well for human teams, it's remarkably hostile to AI agents. As researchers noted: "Breaking down monolithic AI agent architecture into microservices introduces several challenges: coordination overhead, state management, and testing complexity."

**When it makes sense:**

- You already have microservices (don't rewrite)
- Distinct bounded contexts with separate teams
- Scaling requirements genuinely need independent services
- You're building agentic systems with orchestrator-worker patterns

---

**💡 The Microservices Irony**

Here's the thing: microservices excel at scaling teams and systems independently, but they fragment context across network boundaries. Your AI agent suddenly needs to understand multiple repositories, coordinate changes across services, and trace execution through API calls.

**The pragmatic solution:** If you're already running microservices, don't fight it—but DO organize each service internally with Vertical Slice Architecture. Think of it as "microservices for scaling, monorepos for sanity." You get distributed scalability on the outside, AI-friendly structure on the inside.

---

## Pattern 6: Single File / Monolith

**What it is:** Everything in one file (or very few files). The "script" approach.

People absolutely try this—especially new startups "vibe coding" an MVP. It's Friday, you're just prototyping, "I'll clean this up Monday," you think, as you add function number 47 to main.py. Narrator: They did not clean it up Monday.

**Why some teams try it:**

- **Ultimate token efficiency** - AI sees everything at once
- **No navigation** - Everything is right there
- **Fast iteration** - No architectural overhead

**Why it breaks down:**

- **Context window explosion** - Most files hit 1000+ lines quickly
- **No modularity** - Can't work on multiple features in parallel
- **Human maintainability nightmare** - Impossible to navigate for humans
- **Git conflicts** - Every change touches the same file

**When it works:**

- True prototypes (<500 lines total)
- Weekend projects you'll throw away
- Proof-of-concepts where maintainability doesn't matter

**The reality:** I've seen teams try this. It feels productive for the first day. By day three, you're drowning.

## The Context Window Problem: Why Architecture Matters

Here's what many developers miss: **LLMs have limited context windows**, and your architecture determines how much of that window gets wasted on navigation versus actual work.

Current AI coding assistants can process roughly:

- **Fast models**: ~6,000 characters per interaction
- **Advanced models**: ~200,000 tokens (~150K characters)
- **Frontier models**: ~1M tokens (~750K characters)

But a typical enterprise codebase has **millions of tokens** across **thousands of files**.

### The Math on Token Efficiency

**Layered Architecture:**

```
Add product to catalog flow:
- Load controller       (150 tokens)
- Load service         (200 tokens)
- Load repository      (180 tokens)
- Load model          (120 tokens)
- Load validator      (160 tokens)
- Load DTO            (90 tokens)
Total: ~900 tokens just to see the code
```

**Vertical Slice Architecture:**

```
Add product to catalog flow:
- Load products/routes.py    (400 tokens - includes everything)
Total: ~400 tokens
```

**Savings: 55% fewer tokens** for the same understanding. Over hundreds of interactions per day, this compounds massively.

Anthropic's research emphasizes this: "Context is a precious, finite resource. The fundamental goal is finding the smallest set of high-signal tokens that maximize the likelihood of your desired outcome."

## The File Size Factor: Keep It Small

Another critical dimension: **file size**.

AI coding assistants struggle with files over 400-500 lines. Beyond this threshold:

- Context window gets cluttered
- Agent loses track of file structure
- Token efficiency plummets
- Edit accuracy decreases

**Best practices:**

- **Target: <300 lines per file**
- Break large files into focused modules
- One responsibility per file (Single Responsibility Principle)
- Co-locate tests next to implementation

**Example breakdown:**

```
# ❌ Bad: One massive 1200-line file
products/service.py       # Everything in here

# ✅ Good: Broken into focused files
products/
├── service.py            # 200 lines - core business logic
├── validation.py         # 150 lines - input validation
├── pricing.py            # 100 lines - price calculation logic
├── inventory_sync.py     # 120 lines - inventory integration
└── serializers.py        # 180 lines - data transformation
```

Each file is digestible for both AI and humans. The AI can load exactly what it needs, nothing more.

## Documentation Architecture: The Missing Piece

Your code architecture is only half the equation. **Documentation architecture** is equally critical for AI agents.

### The Three-Tier Documentation Model

**Tier 1: README.md** (Single source of truth)

- Project overview and purpose
- Quick start guide (installation, running tests, development server)
- High-level architecture overview
- Common commands and workflows
- Links to deeper documentation

**Tier 2: Feature-level READMEs**

```
products/README.md
inventory/README.md
categories/README.md
```

Each feature directory gets its own README explaining:

- Feature purpose
- Key flows and use cases
- Important edge cases
- Integration points with other features

**Tier 3: Architecture Decision Records (ADRs)**

```
docs/architecture/adr/
├── 001-use-vertical-slice-architecture.md
├── 002-database-per-feature-schema.md
└── 003-authentication-strategy.md
```

ADRs document **why** decisions were made. Critical for AI agents, because without context, they'll suggest reversing decisions they see as suboptimal.

### The AGENTS.md Debate

Recently, some teams started using `AGENTS.md` files—a "README for machines" with AI-specific instructions.

**My take:** If you write a comprehensive README, you don't need AGENTS.md. The content should be identical. As one developer noted: "Your README should be your single source of truth for both humans and AI agents."

If you do use AGENTS.md:

- Keep it ≤150 lines (long files slow agents)
- Include only AI-specific operational notes (build commands, token-efficient summaries)
- Maintain like code—update in same commit when conventions change

## Real-World Case Study: The Refactoring Journey

A startup I advised had 40K lines of Python code in classic layered architecture. Five developers, using GitHub Copilot, constantly frustrated by AI suggestions that didn't understand the codebase.

**Before (Layered Architecture):**

- AI agent needed 6-8 files loaded to make meaningful changes
- Average token usage per change: 12,000 tokens
- Developer satisfaction with AI: 4/10
- Time saved by AI: ~20%

**After (Vertical Slice Architecture):**

- AI agent needed 1-2 files loaded per change
- Average token usage per change: 4,500 tokens
- Developer satisfaction with AI: 8/10
- Time saved by AI: ~60%

**The refactoring took two weeks**. The productivity gains paid for themselves in three weeks.

**How they did it:**

1. Started with new features—built in VSA from day one
2. When touching old code, moved it into feature slices
3. Created migration guide (ADR) explaining the new structure
4. After 6 months, 80% of codebase was in new structure
5. Left stable, untouched code in old structure (pragmatism over purity)

## A Quick Note on Language Choice

Before we dive into migration strategies, a quick note on language choice—because even perfect architecture can't save you from Ruby metaprogramming.

AI agents work best with explicit, straightforward code. The more "magic" in your language (implicit behaviors, heavy metaprogramming, complex type systems), the harder for AI to reason about. Python and Go tend to work well. That said, architecture matters more than language—a well-structured Ruby codebase beats a chaotic Python mess any day.

## Practical Migration Strategies

You can't rewrite your entire codebase overnight. Here's how to migrate pragmatically:

### Strategy 1: New Features First

- All new features use new architecture (VSA or feature folders)
- Old code stays in old structure until touched
- Create clear boundary between old and new
- Over 6-12 months, most active code migrates naturally

### Strategy 2: Feature Extraction

- Pick one feature (e.g., product catalog)
- Extract all related code into new feature directory
- Write feature README
- Update imports and tests
- Deploy and validate
- Repeat with next feature

### Strategy 3: Hybrid Approach

- Keep stable, untouched code in old structure
- Move frequently modified code to new structure
- Create `docs/MIGRATION.md` explaining the two patterns
- Set timeline for eventual full migration (or don't—pragmatism wins)

### Strategy 4: Gradual Layer Collapse

- Start by moving controllers + services into feature folders
- Then add repositories to feature folders
- Finally add models and DTOs
- Each step is a small, safe change

**Pro tip:** Let your AI agent help with the refactoring. Give it the migration plan and have it move files, update imports, and fix tests. It's great at this kind of mechanical work.

## The Dependency Injection Question

Whether you use VSA, feature folders, or modular monolith, you need a strategy for shared dependencies.

**Explicit Dependency Injection (Recommended):**

```python
# ✅ Good: Dependencies are explicit
from fastapi import Depends
from app.database import get_db
from app.logging import get_logger

def create_product(
    request: ProductCreateRequest,
    db: Session = Depends(get_db),
    logger: Logger = Depends(get_logger)
) -> ProductResponse:
    logger.info("Creating product", name=request.name, sku=request.sku)
    product = Product.create(db, request)
    return ProductResponse.from_model(product)
```

**Global Dependencies (Avoid):**

```python
# ❌ Bad: Hidden dependencies
from app.globals import db, logger

def create_product(request: ProductCreateRequest) -> ProductResponse:
    logger.info("Creating product", name=request.name)  # Where does logger come from?
    product = Product.create(db, request)  # Where does db come from?
    return ProductResponse.from_model(product)
```

Why it matters for AI: Remember why explicit dependencies matter? (See [Article 1](link-to-article-1) on architectural boundaries.) FastAPI's `Depends()` makes this perfect—the agent can trace exactly what each function needs.

## The SOLID Principles Debate

Some developers argue that SOLID principles don't matter with AI coding—just have AI generate code and iterate.

**This is wrong.**

Without SOLID principles guiding your architecture:

- AI generates tightly coupled code
- Difficult to test
- Hard to modify without breaking other parts
- Technical debt accumulates fast

SOLID principles are even **more important** with AI, not less. They provide the guard rails that keep AI-generated code maintainable.

**The key SOLID principles for AI coding:**

1. **Single Responsibility Principle** - Keep files focused, one responsibility each
2. **Dependency Inversion** - Depend on abstractions (interfaces), not concrete implementations
3. **Interface Segregation** - Small, focused interfaces rather than large ones

AI agents work better with clean boundaries and explicit contracts. SOLID provides both.

## The Multi-Agent Architecture Connection

If you're building systems with **multiple AI agents** (orchestrator + workers, or agent collaboration patterns), your code architecture becomes even more critical.

**Why:** Each agent operates in its own context window. They need to:

- Find relevant code quickly
- Understand clear boundaries
- Pass information efficiently between agents
- Avoid stepping on each other's toes

**Vertical Slice Architecture is perfect for multi-agent systems** because:

- Each agent can "own" a feature slice
- Clear handoff points between slices
- Minimal context overlap
- Natural work distribution

**Example multi-agent flow:**

```
Orchestrator Agent: "We need to add bulk pricing tiers to the product catalog"
  ↓
Worker Agent 1: "I'll update products/service.py with tier pricing logic"
Worker Agent 2: "I'll update products/pricing.py with calculation engine"
Worker Agent 3: "I'll update products/test_service.py with pricing tests"
  ↓
Orchestrator Agent: "Run tests, merge changes"
```

Each worker operates in a focused context (one feature directory), no conflicts, efficient token usage.

## When to Break the Rules

Architecture patterns are guidelines, not laws. Here's when to deviate:

**Use layered architecture when:**

- Team strongly prefers it and productivity is good
- Application is small (<5K lines) and simple
- You're maintaining legacy code (don't rewrite working systems)
- Regulatory compliance requires specific separation

**Use single-file monolith when:**

- Building weekend proof-of-concept
- True prototype (will be thrown away)
- Educational/learning project

**Use microservices when:**

- Genuinely need independent scaling of services
- Multiple teams with clear bounded contexts
- Already have microservices (incremental improvement > rewrite)

**The principle:** Choose the simplest architecture that solves your problem. Don't over-engineer. But when you're spending 40% of AI token budget on navigation between layers, it's time to reconsider.

## The Token Efficiency Checklist

Before committing to an architecture, audit it against these criteria:

**✅ AI-Friendly Architecture:**

- [ ] Related code lives together (high cohesion)
- [ ] Files are <300 lines each
- [ ] Clear, descriptive file and function names
- [ ] Explicit dependencies (no hidden globals)
- [ ] Feature-level documentation (READMEs)
- [ ] Tests co-located with implementation
- [ ] Straightforward, minimal "magic"
- [ ] Architecture Decision Records for key choices

**❌ AI-Hostile Architecture:**

- [ ] Code scattered across many directories
- [ ] Large files (>500 lines)
- [ ] Generic names (handler.py, utils.py, helpers.py)
- [ ] Hidden dependencies and global state
- [ ] Documentation scattered or missing
- [ ] Tests in separate tree far from code
- [ ] Heavy metaprogramming or implicit behaviors
- [ ] No explanation of architectural choices

## Getting Started: Your First Steps

Don't try to implement perfect architecture on day one. Start small, learn, iterate.

**Week 1: Audit**

- Map your current architecture
- Identify pain points (where does AI struggle most?)
- Measure token usage for common operations
- Survey team on AI productivity

**Week 2: Experiment**

- Pick one new feature
- Implement in Vertical Slice Architecture
- Measure token efficiency vs old approach
- Gather team feedback

**Week 3: Expand**

- Apply to 2-3 more new features
- Create migration guide (ADR)
- Update documentation
- Share learnings with team

**Week 4+: Scale**

- All new features use new architecture
- Gradually migrate high-traffic code
- Set up monitoring for AI productivity
- Iterate based on data

**Most important:** Get the team bought in. Architecture changes fail when imposed top-down. Run experiments, share data, let results speak.

## Conclusion: Architecture Is Infrastructure

You wouldn't run a production application without proper infrastructure—load balancers, databases, caching, monitoring. **Architecture for AI coding is infrastructure for your development process**.

The architecture patterns you choose create the environment where both AI and humans work. Choose poorly, and you'll fight your codebase every day. Choose well, and your AI agents become 3-5× more productive.

The winners in AI-augmented development aren't the teams with better prompts or fancier AI tools. They're the teams with **better architecture**.

Here's the decision matrix one more time:

| Pattern              | AI-Friendliness | Token Efficiency | Maintainability | Complexity | Best For                      |
| -------------------- | --------------- | ---------------- | --------------- | ---------- | ----------------------------- |
| **Vertical Slice**   | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐⭐       | ⭐⭐⭐⭐        | ⭐⭐       | New apps, AI-heavy teams      |
| **Feature Folders**  | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐         | ⭐⭐⭐⭐        | ⭐⭐       | Transitioning from layered    |
| **Modular Monolith** | ⭐⭐⭐⭐        | ⭐⭐⭐⭐         | ⭐⭐⭐⭐        | ⭐⭐⭐     | Large apps, strict boundaries |
| **Layered**          | ⭐⭐⭐          | ⭐⭐             | ⭐⭐⭐⭐⭐      | ⭐⭐⭐     | Small apps, legacy code       |
| **Microservices**    | ⭐⭐            | ⭐⭐             | ⭐⭐⭐          | ⭐⭐⭐⭐⭐ | Already using, scaling needs  |
| **Single File**      | ⭐⭐            | ⭐⭐⭐⭐⭐       | ⭐              | ⭐         | Prototypes only               |

**My recommendation:** Start with Vertical Slice Architecture. It's the sweet spot—high AI productivity, reasonable complexity, good maintainability. You can always adjust later based on your specific needs.

As you build your next project, remember: **The goal isn't to organize code for compilers or humans alone—it's to organize code for human-AI collaboration**.

---

**About the Author**

Rasmus Widing is a Product Builder and AI adoption specialist who has been using AI to build agents, automations, and web apps for over three years. He created the PRP (Product Requirements Prompts) framework for agentic engineering, now used by hundreds of engineers. He helps teams adopt AI through systematic frameworks, workshops, and training at [rasmuswiding.com](https://rasmuswiding.com).

_Want to dive deeper? Check out my PRP framework on GitHub: [github.com/Wirasm/PRPs-agentic-eng](https://github.com/Wirasm/PRPs-agentic-eng)_
