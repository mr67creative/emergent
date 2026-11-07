def new_profile():
    return {'name':'Alex Morgan', 'balance_mills':14850, 'views':342, 'seconds':13260, 'referral_mills':2850,
            'interests':['AI / ML','Programming','Hardware'], 'discovered':{'Systems':44,'Science':28},
            'bookmarks':[], 'upvotes':[], 'reads':[], 'source_clicks':[], 'claims':{}, 'transactions':[], 'reviewed':[], 'decisions':[]}

INSIGHTS = [
 {'id':'kv-cache','title':'The hidden memory cost of every token.','topic':'AI / ML','seconds':30,'author':'The inference notebook','likes':128,'visual':'ai',
  'body':'Every generated token carries a memory cost. Transformers cache attention keys and values so they do not have to recompute the entire conversation at each step.\n\nThis KV cache grows with sequence length, layer count, batch size, and attention heads. At long context lengths, it can compete with the model weights for GPU memory.\n\nGrouped-query attention shares keys and values across query heads. Quantized caches and paged allocation reduce the footprint further. The trade-off is not simply speed versus quality: serving more concurrent users can depend on memory efficiency first.',
  'source':'https://huggingface.co/docs/transformers/kv_cache'},
 {'id':'postgres','title':'Ship the index. Skip the downtime.','topic':'Systems','seconds':30,'author':'Systems, simplified','likes':96,'visual':'systems',
  'body':'CREATE INDEX CONCURRENTLY lets PostgreSQL build an index without blocking ordinary inserts, updates, and deletes.\n\nThe catch: it does more work than a standard build, performs multiple table scans, and cannot run inside a transaction block. A failed build may leave an invalid index that still creates write overhead.\n\nCheck pg_index.indisvalid after a failed operation, remove invalid leftovers, and schedule large builds with I/O capacity in mind. Concurrent does not mean free.',
  'source':'https://www.postgresql.org/docs/current/sql-createindex.html'},
 {'id':'chip','title':'Why the fastest chip waits for memory.','topic':'Hardware','seconds':60,'author':'Silicon field notes','likes':84,'visual':'hardware',
  'body':'Modern processors can execute instructions faster than main memory can supply data. This gap is the memory wall.\n\nCaches keep recently used data close to the compute units. Access patterns with good spatial and temporal locality benefit most. A tight loop over contiguous arrays can outperform pointer-heavy structures even with the same theoretical complexity.\n\nBefore optimizing arithmetic, measure cache misses and memory bandwidth. Sometimes the best performance improvement is changing how data is laid out.',
  'source':'https://en.wikipedia.org/wiki/Memory_wall'},
 {'id':'bayes','title':'A better way to change your mind.','topic':'Math','seconds':30,'author':'The useful equation','likes':67,'visual':'math',
  'body':'Bayes’ theorem turns a prior belief into a posterior belief using evidence. Posterior odds equal prior odds multiplied by the likelihood ratio.\n\nA positive result is not automatically a high probability of the event: base rates matter. A rare event can still be unlikely after a moderately accurate test.\n\nThe practical lesson is to ask two questions: how common was the event before this evidence, and how much more likely is this evidence if the event is true?',
  'source':'https://en.wikipedia.org/wiki/Bayes%27_theorem'},
 {'id':'cold-start','title':'Your first ten users are the product.','topic':'Startups','seconds':60,'author':'Zero to useful','likes':112,'visual':'startup',
  'body':'Early users expose the gap between the problem you imagined and the one they actually have. At this stage, depth beats reach.\n\nWatch someone complete a real task. Record where they pause, what they work around, and what they do after leaving your product. Interviews tell you what users say; observation tells you what they do.\n\nBuild a feedback loop around a narrow group with a repeated problem. Retention is a stronger signal than an enthusiastic first impression.',
  'source':'https://www.ycombinator.com/library'},
 {'id':'spec-decode','title':'Two models. One faster answer.','topic':'AI / ML','seconds':180,'author':'The inference notebook','likes':153,'visual':'decode',
  'body':'Speculative decoding uses a small draft model to propose several tokens, then asks a larger target model to verify them in parallel.\n\nWhen the draft agrees with the target often enough, the target performs fewer expensive sequential steps. Exact speculative sampling can preserve the target distribution, rather than approximating it.\n\nSpeedups depend on acceptance rate, draft-model cost, hardware, and workload. A larger draft is not always better: its extra latency may erase the savings. This is especially relevant when inference is memory-bound.',
  'source':'https://arxiv.org/abs/2211.17192'},
]

REVIEWS = [
 {'id':'seed-1','kind':'ad','brand':'Linear','headline':'Build things that move you forward.','description':'The issue tracker built for teams that ship.','cta':'Try Linear','risk':28,'fraud':12,'copy':38,'url_safety':99},
 {'id':'seed-2','kind':'insight','brand':'PlanetScale','headline':'Indexes are a trade, not a free lunch.','description':'Every index speeds up selected reads and adds work to writes. Measure your query patterns before adding one.','cta':'Read insight','risk':16,'fraud':7,'copy':14,'url_safety':99},
 {'id':'seed-3','kind':'ad','brand':'CloudStack','headline':'Your next deployment, minus the friction.','description':'From a pull request to production in seconds.','cta':'Explore','risk':54,'fraud':32,'copy':66,'url_safety':92},
 {'id':'seed-4','kind':'ad','brand':'QuickYield','headline':'Guaranteed returns. Zero risk.','description':'Double your balance with our secret trading engine.','cta':'Join now','risk':94,'fraud':96,'copy':98,'url_safety':22},
]