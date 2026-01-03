-- 1. Create Favorites Table
create table public.favorites (
  user_id uuid references auth.users not null,
  article_id bigint references public.articles(id) on delete cascade not null,
  created_at timestamptz default now(),
  primary key (user_id, article_id)
);

-- 2. Create Read Later Table
create table public.read_laters (
  user_id uuid references auth.users not null,
  article_id bigint references public.articles(id) on delete cascade not null,
  created_at timestamptz default now(),
  primary key (user_id, article_id)
);

-- 3. Add Indexes (for faster queries, e.g., "find all articles favorited by a user")
create index favorites_user_id_idx on public.favorites(user_id);
create index read_laters_user_id_idx on public.read_laters(user_id);

-- Enable RLS
alter table public.favorites enable row level security;
alter table public.read_laters enable row level security;

-- Policy: Users can view their own favorites
create policy "Users can view their own favorites" 
on public.favorites for select 
to authenticated 
using (auth.uid() = user_id);

-- Policy: Users can add their own favorites
create policy "Users can add their own favorites" 
on public.favorites for insert 
to authenticated 
with check (auth.uid() = user_id);

-- Policy: Users can remove their own favorites
create policy "Users can remove their own favorites" 
on public.favorites for delete 
to authenticated 
using (auth.uid() = user_id);

-- Read Later policies are similar to Favorites
create policy "Users can view their own read_laters" 
on public.read_laters for select 
to authenticated 
using (auth.uid() = user_id);

create policy "Users can add their own read_laters" 
on public.read_laters for insert 
to authenticated 
with check (auth.uid() = user_id);

create policy "Users can remove their own read_laters" 
on public.read_laters for delete 
to authenticated 
using (auth.uid() = user_id);