#!/usr/bin/env bash
# Preset: Ruby on Rails with Hotwire

preset_name="ruby-rails"
preset_description="Ruby 3.3+ / Rails 7.2+ backend with Hotwire (Turbo + Stimulus), PostgreSQL, RSpec testing"

# Rules files: newline-delimited "filename|description" pairs
RULES_FILES="api-contracts.md|Rails API controllers, jbuilder/AMS serialization, strong parameters, routing, versioned APIs
database.md|ActiveRecord models, migrations, associations, scopes, N+1 prevention, counter caches
cross-service.md|Rails conventions, service objects, Hotwire patterns, RuboCop, testing with RSpec"

# Technology stack entries
TECH_STACK="| Backend | Ruby 3.3+, Rails 7.2+ |
| Frontend | Hotwire (Turbo + Stimulus), Import Maps / esbuild |
| Database | PostgreSQL 16+ |
| Testing | RSpec, FactoryBot, Capybara, SimpleCov |
| Linting | RuboCop (rails, rspec, performance cops) |
| Auth | Devise / custom \`has_secure_password\` |
| Background Jobs | Solid Queue / Sidekiq |"

# Context loading table entries
CONTEXT_LOADING_TABLE="| **New API endpoint** | \`.claude/rules/api-contracts.md\`, \`app/controllers/\` |
| **Database changes** | \`.claude/rules/database.md\`, \`app/models/\`, \`db/migrate/\` |
| **Hotwire / frontend** | \`.claude/rules/cross-service.md\` (Hotwire section), \`app/views/\`, \`app/javascript/\` |
| **Debugging** | \`.claude/rules/troubleshooting.md\` |
| **Architecture decisions** | \`docs/decisions/index.md\` |
| **Service objects** | \`.claude/rules/cross-service.md\`, \`app/services/\` |"

# Context groups
CONTEXT_GROUPS='### `api`
Read: `.claude/rules/api-contracts.md`, `app/controllers/api/`, `app/serializers/`

### `database`
Read: `.claude/rules/database.md`, `app/models/`, `db/schema.rb`

### `hotwire`
Read: `.claude/rules/cross-service.md` (Hotwire section), `app/views/`, `app/javascript/controllers/`

### `debug`
Read: `.claude/rules/troubleshooting.md`'

# Development workflow
WORKFLOW='```bash
# Setup
bin/setup                         # runs bundle, db:prepare, etc.
bundle install && rails db:create db:migrate db:seed

# Run dev server
bin/dev                           # uses Procfile.dev (foreman/overmind)

# Run tests
bundle exec rspec
bundle exec rspec spec/requests/  # request specs only

# Lint
bundle exec rubocop
bundle exec rubocop -A            # auto-correct all

# Database
rails db:migrate
rails db:rollback STEP=1
rails db:migrate:status

# Console
rails console --sandbox           # rolls back all changes on exit

# Generate
rails generate scaffold User name:string email:string
rails generate migration AddIndexToUsersEmail
rails generate stimulus search
```

### Development URLs

- Application: `http://localhost:3000`
- Letter Opener (emails): `http://localhost:3000/letter_opener`'

# Project overview
PROJECT_OVERVIEW="Rails 7.2+ application with Hotwire for interactive UI. API endpoints under \`/api/v1/\`, HTML views served by standard controllers."

# Workspace structure
WORKSPACE_STRUCTURE='{{PROJECT_NAME}}/
├── CLAUDE.md
├── .claude/
│   ├── rules/
│   │   ├── api-contracts.md
│   │   ├── database.md
│   │   ├── cross-service.md
│   │   └── troubleshooting.md
│   ├── hooks/
│   │   └── lint-on-edit.sh
│   ├── memory/
│   │   ├── MEMORY.md
│   │   ├── rails-patterns.md
│   │   ├── database-gotchas.md
│   │   └── debugging.md
│   └── commands/
│       ├── review.md
│       ├── test.md
│       ├── plan.md
│       ├── smoke.md
│       └── lint.md
├── app/
│   ├── controllers/
│   │   ├── application_controller.rb
│   │   └── api/v1/
│   ├── models/
│   ├── views/layouts/
│   ├── services/
│   ├── serializers/
│   ├── javascript/controllers/  # Stimulus controllers
│   ├── jobs/
│   └── mailers/
├── config/
│   ├── routes.rb
│   ├── database.yml
│   └── initializers/
├── db/
│   ├── migrate/
│   ├── schema.rb
│   └── seeds.rb
├── spec/
│   ├── models/
│   ├── requests/
│   ├── services/
│   ├── factories/
│   └── spec_helper.rb
├── docs/
│   ├── plans/
│   │   └── .plan-template.md
│   └── decisions/
│       ├── index.md
│       └── adr-template.md
├── scripts/
│   └── smoke-rails.sh
├── Gemfile
└── Gemfile.lock'

# Smoke test scripts: "filename|title|checks_variable_name"
SMOKE_SCRIPTS="smoke-rails.sh|Rails Health Checks|SMOKE_RAILS_CHECKS"

# shellcheck disable=SC2034
SMOKE_RAILS_CHECKS='section "Application"

if [[ -f "config/application.rb" ]]; then
  pass "config/application.rb exists"
else
  fail "config/application.rb not found — not a Rails project?"
fi

if [[ -f "Gemfile.lock" ]]; then
  pass "Gemfile.lock exists"
else
  fail "Gemfile.lock missing — run bundle install"
fi

if command -v ruby >/dev/null 2>&1; then
  ruby_version=$(ruby -e "puts RUBY_VERSION")
  if [[ "${ruby_version%%.*}" -ge 3 ]]; then
    pass "Ruby ${ruby_version} installed"
  else
    warn "Ruby ${ruby_version} found — 3.3+ recommended"
  fi
else
  fail "Ruby not installed"
fi

section "Database"

if rails db:migrate:status 2>/dev/null | grep -q "up"; then
  pass "Database migrations applied"
else
  warn "Database may need migration — run: rails db:migrate"
fi

section "Dependencies"

if bundle check >/dev/null 2>&1; then
  pass "All gems installed"
else
  warn "Gems missing — run: bundle install"
fi

section "Linting"

if command -v rubocop >/dev/null 2>&1; then
  offense_count=$(bundle exec rubocop --format simple 2>/dev/null | tail -1 | grep -oE "[0-9]+ offense" | grep -oE "[0-9]+")
  if [[ "${offense_count:-0}" -eq 0 ]]; then
    pass "RuboCop passes with no offenses"
  else
    warn "RuboCop found ${offense_count} offense(s)"
  fi
else
  warn "RuboCop not installed — add to Gemfile"
fi

section "Tests"

if [[ -d "spec" ]]; then
  if bundle exec rspec --dry-run 2>/dev/null | grep -q "example"; then
    pass "RSpec specs discovered"
  else
    warn "No RSpec examples found"
  fi
elif [[ -d "test" ]]; then
  pass "Minitest directory exists"
else
  warn "No test directory found (spec/ or test/)"
fi'

# Troubleshooting sections
TROUBLESHOOTING_SECTIONS='## 1. Rails Server / Boot

### Symptom: `PG::ConnectionBad: could not connect to server`

**Diagnosis:** PostgreSQL is not running or credentials in `config/database.yml` are wrong.

**Fix:**
```bash
pg_isready                              # check if PG is running
brew services start postgresql@16       # macOS Homebrew
rails db:create                         # create DB if it does not exist
```

---

### Symptom: `Migrations are pending. To resolve this issue, run: bin/rails db:migrate`

**Diagnosis:** Unapplied migrations in `db/migrate/`. Rails raises `ActiveRecord::PendingMigrationError`.

**Fix:**
```bash
rails db:migrate
rails db:migrate:status       # check which are up/down
rails db:rollback STEP=1      # undo last migration if broken
```

---

## 2. ActiveRecord / Database

### Symptom: N+1 queries detected by Bullet gem (or slow page loads)

**Diagnosis:** Associated records loaded one-at-a-time inside a loop.

**Fix:**
```ruby
# Bad — N+1:
Post.all.each { |p| puts p.user.name }
# Good — eager-load:
Post.includes(:user).each { |p| puts p.user.name }
# For WHERE on association:
Post.eager_load(:comments).where(comments: { approved: true })
```

---

### Symptom: `ActiveRecord::RecordNotUnique` on insert

**Diagnosis:** Unique DB constraint violated (e.g., duplicate email).

**Fix:**
```ruby
validates :email, uniqueness: { case_sensitive: false }  # model validation
# Handle race condition:
begin
  @user = User.create!(user_params)
rescue ActiveRecord::RecordNotUnique
  @user = User.find_by(email: user_params[:email])
end
```

---

## 3. Hotwire / Turbo

### Symptom: Form submission replaces entire page instead of Turbo Frame

**Diagnosis:** Response missing matching `<turbo-frame>` tag. Turbo falls back to full page replace.

**Fix:**
```erb
<%= turbo_frame_tag "edit_user" do %>
  <%= form_with(model: @user) do |f| %>
    ...
  <% end %>
<% end %>
<%# Response must also contain turbo_frame_tag with same ID %>
```

---

## 4. Testing

### Symptom: `FactoryBot::InvalidFactoryError` or factory traits not found

**Diagnosis:** Factory definitions missing or have circular association dependencies.

**Fix:**
```bash
bundle exec rake factory_bot:lint  # lint all factories
# Common cause: factory references association whose factory does not exist
```

---

*Add entries as you encounter and solve issues. Use the Symptom -> Diagnosis -> Fix format.*'

# Memory topics: "filename|description" pairs
MEMORY_TOPICS="rails-patterns.md|Controller patterns, service objects, Hotwire conventions, route design
database-gotchas.md|Migration issues, N+1 gotchas, ActiveRecord edge cases, index strategies
debugging.md|Common errors encountered and their solutions"

# Slash commands to scaffold
COMMANDS="review.md
test.md
plan.md
smoke.md
lint.md"

# --- Substantive Rules Content ---

# shellcheck disable=SC2034
RULES_CONTENT_API_CONTRACTS='# API Contracts

> **When to use:** Adding or modifying API controllers, debugging request/response issues, versioning APIs.
>
> **Read first for:** Any API endpoint work, serializer changes, authentication flows.

## Routing Conventions

```ruby
# config/routes.rb
Rails.application.routes.draw do
  namespace :api do
    namespace :v1 do
      resources :users, only: [:index, :show, :create, :update, :destroy] do
        resources :posts, only: [:index, :create], shallow: true
      end
      resource :session, only: [:create, :destroy]
    end
  end
  root "pages#home"
  resources :users
end
```

**Rules:**
- API endpoints live under `Api::V1::` namespace — never mix HTML and API controllers
- Use `resources` / `resource` for RESTful routes — avoid custom routes unless necessary
- `shallow: true` for nested resources with unique IDs
- New API versions get a new namespace (`Api::V2::`) — never break v1 contracts

## Authentication

```ruby
# app/controllers/api/v1/base_controller.rb
module Api::V1
  class BaseController < ActionController::API
    before_action :authenticate_user!

    private

    def authenticate_user!
      token = request.headers["Authorization"]&.split(" ")&.last
      @current_user = User.find_by_auth_token(token)
      render json: { error: "Unauthorized" }, status: :unauthorized unless @current_user
    end
  end
end
```

## Controller Pattern

```ruby
# app/controllers/api/v1/users_controller.rb
module Api::V1
  class UsersController < BaseController
    def index
      @users = User.active.order(created_at: :desc).page(params[:page]).per(25)
      render json: @users, each_serializer: UserSerializer, meta: pagination_meta(@users)
    end

    def create
      @user = User.new(user_params)
      if @user.save
        render json: @user, serializer: UserSerializer, status: :created
      else
        render json: { errors: @user.errors.full_messages }, status: :unprocessable_entity
      end
    end

    private

    def user_params
      params.require(:user).permit(:name, :email, :role)
    end
  end
end
```

**Strong parameters:** Always `params.require(:model).permit(...)` — never `params.permit!`.
Nested: `permit(address_attributes: [:street, :city])`. Arrays: `permit(tag_ids: [])`.

## Serialization

```ruby
# AMS — app/serializers/user_serializer.rb
class UserSerializer < ActiveModel::Serializer
  attributes :id, :name, :email, :role, :created_at
  has_many :posts, serializer: PostSummarySerializer
  def created_at
    object.created_at.iso8601
  end
end

# jbuilder — app/views/api/v1/users/show.json.jbuilder
json.id @user.id
json.name @user.name
json.posts @user.posts, partial: "api/v1/posts/post", as: :post
```

## Rack Middleware

```ruby
# config/application.rb
config.middleware.insert_before 0, Rack::Cors do
  allow do
    origins ENV.fetch("CORS_ORIGINS", "http://localhost:3000").split(",")
    resource "/api/*", headers: :any,
      methods: [:get, :post, :put, :patch, :delete, :options], max_age: 600
  end
end
```

## Error Response Format

| Status | When |
|--------|------|
| 401 | Missing or invalid token |
| 403 | Valid token, insufficient permissions |
| 404 | Resource not found |
| 422 | Validation failed (ActiveRecord errors) |
| 429 | Rate limited (Rack::Attack) |

## Health Endpoints

```ruby
get "/health", to: proc { [200, {}, ["ok"]] }
get "/ready",  to: "health#ready"
```'

# shellcheck disable=SC2034
RULES_CONTENT_DATABASE='# Database Patterns

> **When to use:** Schema changes, new models, migration work, debugging query performance.
>
> **Read first for:** Any database-related task, association changes, index additions.

## Migrations

```bash
rails generate migration AddIndexToUsersEmail
rails generate migration CreateOrders user:references total:decimal status:integer
rails db:migrate
rails db:migrate:status
rails db:rollback STEP=1
```

**Rules:**
- Never edit a migration merged to main — create a new one
- Always add indexes for foreign keys and WHERE/ORDER BY columns
- Use `change` for reversible; `up`/`down` for irreversible
- Add `null: false` constraints explicitly

## Model Pattern

```ruby
class User < ApplicationRecord
  has_many :posts, dependent: :destroy
  has_one :profile, dependent: :destroy

  validates :name, presence: true, length: { maximum: 100 }
  validates :email, presence: true, uniqueness: { case_sensitive: false },
                    format: { with: URI::MailTo::EMAIL_REGEXP }

  scope :active, -> { where(active: true) }
  scope :recently_created, -> { where("created_at > ?", 30.days.ago) }
  scope :by_role, ->(role) { where(role: role) }

  before_validation :normalize_email
  after_create_commit :send_welcome_email

  enum :role, { member: 0, admin: 1, superadmin: 2 }, prefix: true

  private

  def normalize_email
    self.email = email&.downcase&.strip
  end
end
```

## N+1 Prevention

```ruby
# BAD — N+1:
Post.all.each { |p| puts p.user.name }

# includes — LEFT OUTER JOIN or 2 queries
Post.includes(:user).each { |p| puts p.user.name }

# preload — always 2 separate queries
Post.preload(:user, :comments).all

# eager_load — single JOIN, needed for WHERE on association
Post.eager_load(:comments).where(comments: { approved: true })

# Deep nesting
Post.includes(comments: :user).all
```

Use `bullet` gem in development to detect N+1 automatically.

## Counter Caches

```ruby
# migration:
add_column :users, :posts_count, :integer, default: 0, null: false
# model:
belongs_to :user, counter_cache: true
# Now User#posts_count maintained automatically — no COUNT query
```

## Query Patterns

```ruby
User.active.order(created_at: :desc).page(params[:page]).per(25)      # pagination
User.find_or_create_by!(email: "admin@ex.com") { |u| u.name = "Admin" }
User.find_each(batch_size: 1000) { |u| u.update_stats! }             # batch
User.where("created_at > :date", date: 1.week.ago)                   # safe SQL
# NEVER: User.where("role = '\''#{params[:role]}'\''") — SQL injection!
```

## Schema Conventions

- Table names: lowercase plural (`users`, `order_items`)
- Primary keys: `id` (bigint auto-increment)
- Timestamps: `created_at`, `updated_at` (via `t.timestamps`)
- Foreign keys: `<table_singular>_id` (e.g., `user_id`)
- Indexes: `index_<table>_on_<columns>` (Rails default naming)'

# shellcheck disable=SC2034
RULES_CONTENT_CROSS_SERVICE='# Cross-Service Patterns

> **When to use:** Ensuring consistency, understanding Rails conventions, Hotwire patterns.
>
> **Read first for:** Service objects, Turbo/Stimulus work, testing conventions.

## Rails Conventions

- Follow **Convention over Configuration** — do not override defaults without strong reason
- Actions: `index`, `show`, `new`, `create`, `edit`, `update`, `destroy`
- Fat models, skinny controllers — but extract complex logic to service objects (`app/services/`)

## Service Objects

```ruby
# app/services/users/register.rb
module Users
  class Register
    def initialize(params:, invited_by: nil)
      @params = params
      @invited_by = invited_by
    end

    def call
      user = User.new(@params)
      ActiveRecord::Base.transaction do
        user.save!
        Profile.create!(user: user)
      end
      ServiceResult.new(success: true, data: user)
    rescue ActiveRecord::RecordInvalid => e
      ServiceResult.new(success: false, errors: e.record.errors.full_messages)
    end
  end
end
```

## Hotwire: Turbo Frames

```erb
<%= turbo_frame_tag "users_list" do %>
  <% @users.each do |user| %>
    <%= render partial: "user", locals: { user: user } %>
  <% end %>
<% end %>

<%= turbo_frame_tag dom_id(user) do %>
  <div class="user-card">
    <h3><%= user.name %></h3>
    <%= link_to "Edit", edit_user_path(user) %>
  </div>
<% end %>
```

- Every `turbo_frame_tag` needs a unique ID (use `dom_id(model)`)
- Use `data-turbo-frame="_top"` to break out of a frame

## Hotwire: Turbo Streams

```erb
<%# app/views/users/create.turbo_stream.erb %>
<%= turbo_stream.prepend "users_list" do %>
  <%= render partial: "user", locals: { user: @user } %>
<% end %>
<%= turbo_stream.update "user_count", html: User.count.to_s %>
```

Actions: `append`, `prepend`, `replace`, `update`, `remove`, `before`, `after`.

## Hotwire: Stimulus Controllers

```javascript
// app/javascript/controllers/search_controller.js
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input", "results"]
  static values = { url: String }

  search() {
    clearTimeout(this.timeout)
    this.timeout = setTimeout(() => {
      fetch(`${this.urlValue}?q=${this.inputTarget.value}`, {
        headers: { "Accept": "text/vnd.turbo-stream.html" }
      })
        .then(r => r.text())
        .then(html => Turbo.renderStreamMessage(html))
    }, 300)
  }

  disconnect() { clearTimeout(this.timeout) }
}
```

```erb
<div data-controller="search" data-search-url-value="<%= search_users_path %>">
  <input data-search-target="input" data-action="input->search#search">
</div>
```

## Testing with RSpec

```ruby
# spec/models/user_spec.rb
RSpec.describe User, type: :model do
  it { is_expected.to validate_presence_of(:name) }
  it { is_expected.to have_many(:posts).dependent(:destroy) }

  describe ".active" do
    it "returns only active users" do
      active = create(:user, active: true)
      create(:user, active: false)
      expect(User.active).to eq([active])
    end
  end
end

# spec/requests/api/v1/users_spec.rb
RSpec.describe "Api::V1::Users", type: :request do
  let(:user) { create(:user) }
  let(:headers) { { "Authorization" => "Bearer #{user.auth_token}" } }

  it "returns paginated users" do
    create_list(:user, 3)
    get "/api/v1/users", headers: headers
    expect(response).to have_http_status(:ok)
  end
end

# spec/factories/users.rb
FactoryBot.define do
  factory :user do
    name { Faker::Name.name }
    email { Faker::Internet.unique.email }
    trait :admin do
      role { :admin }
    end
    trait :with_posts do
      after(:create) { |u| create_list(:post, 3, user: u) }
    end
  end
end
```

## Environment Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `DATABASE_URL` | `.env` / Secret | PostgreSQL connection string |
| `SECRET_KEY_BASE` | `rails credentials:edit` | Session signing key |
| `RAILS_MASTER_KEY` | Secret | Decrypts credentials.yml.enc |
| `REDIS_URL` | Config | Redis for caching, Action Cable, Sidekiq |

Use `rails credentials:edit` for production secrets — never `.env` in production.

## Caching

```ruby
Rails.cache.fetch("user_stats/#{user.id}", expires_in: 1.hour) do
  user.compute_stats
end
```

## Security Best Practices

### Input Validation
- Validate ALL user input at API boundaries using strong parameters (`params.require(:model).permit(...)`)
- Add model-level validations: `validates :email, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }`
- Never use `params.permit!` — always use explicit allowlist of permitted attributes
- Reject unexpected fields — strong parameters raise on unpermitted params in strict mode

```ruby
def user_params
  params.require(:user).permit(:name, :email, :role)
end
```

### SQL Injection Prevention
- NEVER concatenate user input into queries
- Use ActiveRecord parameterized queries or hash conditions

```ruby
# SAFE — parameterized query
User.where("email = ?", email)
User.where(email: email)

# SAFE — named placeholders
User.where("role = :role AND active = :active", role: params[:role], active: true)

# UNSAFE — string interpolation (NEVER do this)
# User.where("email = '\''#{params[:email]}'\''")
```

### Rate Limiting
- Use `rack-attack` gem for rate limiting at the Rack middleware level
- Apply stricter limits to auth endpoints (5 requests/min) and general API (100 requests/min)

```ruby
# config/initializers/rack_attack.rb
Rack::Attack.throttle("auth/ip", limit: 5, period: 60.seconds) do |req|
  req.ip if req.path.start_with?("/api/v1/auth")
end

Rack::Attack.throttle("api/ip", limit: 100, period: 60.seconds) do |req|
  req.ip if req.path.start_with?("/api/")
end
```

### CORS Configuration
- Use `rack-cors` gem — never use `origins "*"` in production
- Whitelist specific origins

```ruby
# config/application.rb
config.middleware.insert_before 0, Rack::Cors do
  allow do
    origins ENV.fetch("CORS_ORIGINS", "https://app.example.com").split(",")
    resource "/api/*", headers: :any,
      methods: [:get, :post, :put, :patch, :delete, :options],
      credentials: true, max_age: 600
  end
end
```

### Secrets Management
- Never commit secrets to git — use `rails credentials:edit` for encrypted secrets
- Use `RAILS_MASTER_KEY` environment variable in production to decrypt `credentials.yml.enc`
- Rotate secrets immediately on suspected compromise — re-encrypt credentials with new key

### Dependency Scanning
- Run `bundle audit` in CI on every PR to detect known vulnerabilities (`bundler-audit` gem)
- Run `brakeman` for static analysis of Rails-specific security issues
- Enable Dependabot or Renovate for automated gem dependency updates

### HTTPS / TLS
- Enforce HTTPS in production with `config.force_ssl = true` in `config/environments/production.rb`
- This automatically sets HSTS header: `Strict-Transport-Security: max-age=63072000; includeSubDomains`
- Configure `config.assume_ssl = true` when behind a TLS-terminating reverse proxy

## Performance Checklist

### Database Performance
- Prevent N+1 queries: use `includes()`, `preload()`, or `eager_load()` for associations
- Use `bullet` gem in development to automatically detect N+1 queries
- Add database indexes in migrations for frequently queried columns (`add_index :users, :email, unique: true`)
- Use connection pooling — configure `pool` size in `config/database.yml` (default: 5, increase for production)
- Profile slow queries with `EXPLAIN ANALYZE` via `ActiveRecord::Base.connection.explain()`

### Caching Strategy
- Use `Rails.cache.fetch` with Redis (`CACHE_STORE=redis_cache_store` in production)
- Cache expensive computations and external API responses with TTL
- Use Russian Doll caching for nested view fragments

```ruby
Rails.cache.fetch("user:#{user.id}", expires_in: 5.minutes) do
  user.as_json(include: :profile)
end

Rails.cache.delete("user:#{user.id}") # invalidate on update
```

### API Response Optimization
- Always paginate list endpoints using `kaminari` or `pagy` gems
- Compress responses: enable gzip in web server (nginx) or use `Rack::Deflater` middleware
- Set appropriate `Cache-Control` headers for cacheable responses with `expires_in` or `stale?`
- Use `select()` to limit columns and serializers to control response shape'

LINT_LANGUAGES="Ruby (rubocop), ERB (erb_lint), YAML, Shell (shellcheck)"
