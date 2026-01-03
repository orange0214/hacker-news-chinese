create or replace function public.handle_new_favorite()
returns trigger as $$
begin
  update public.articles
  set favorites_count = favorites_count + 1
  where id = new.article_id;
  return new;
end;
$$ language plpgsql security definer;

create or replace function public.handle_unfavorite()
returns trigger as $$
begin
  update public.articles
  set favorites_count = favorites_count - 1
  where id = old.article_id;
  return old;
end;
$$ language plpgsql security definer;

create trigger on_favorite_added
  after insert on public.favorites
  for each row execute procedure public.handle_new_favorite();

create trigger on_favorite_removed
  after delete on public.favorites
  for each row execute procedure public.handle_unfavorite();