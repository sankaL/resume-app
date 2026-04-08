begin;

alter type public.failure_reason_enum add value if not exists 'generation_timeout';
alter type public.failure_reason_enum add value if not exists 'generation_cancelled';

commit;
