const OPENERS = [
  "Summoning",
  "Consulting",
  "Aligning",
  "Routing",
  "Dispatching",
  "Persuading",
  "Negotiating with",
  "Synchronizing",
  "Cross-checking",
  "Decoding",
  "Dusting off",
  "Interpreting",
  "Calibrating",
  "Scanning",
  "Shuffling",
];

const AGENTS = [
  "the Sims mailroom",
  "the Civ strategy council",
  "oracle pigeons",
  "the llama librarian",
  "the GPU spirits",
  "the archive keepers",
  "the crystal clerks",
  "the token druids",
  "the cosmic interns",
  "the probability monks",
  "the silicon sages",
  "the latency goblins",
  "the parchment operators",
  "the branch predictors",
  "the whisper network",
];

const ACTIONS = [
  "for a dignified reply",
  "for better context",
  "for a cleaner prophecy",
  "for a wiser interpretation",
  "for a high-confidence omen",
  "for a legally distinct miracle",
  "for premium oracle energy",
  "for a strategic answer",
  "for maximum mystical throughput",
  "for an elegant token trail",
  "for a surprisingly coherent vision",
  "for stable inference vibes",
  "for a fully enchanted response",
  "for an archival-quality insight",
  "for a smoother computational ritual",
];

const ENDINGS = [
  "Please hold the thought bubble.",
  "No peasants were taxed during this process.",
  "The candles are decorative, mostly.",
  "The llama requested another second.",
  "The bureaucracy insists this is normal.",
  "A prophecy stamp is being applied.",
  "We are absolutely making progress.",
  "The council is pretending to be efficient.",
  "Results are being polished with moonlight.",
  "Someone in the archive yelled 'found it!'.",
  "The oracle assures us this is intentional.",
  "A tiny fanfare may or may not play soon.",
  "The tokens are walking in single file.",
  "This turn should finish shortly.",
  "A clerk is dramatically flipping pages.",
];

const TOPIC_ACTIONS = [
  "searching public records about",
  "reviewing encyclopedia notes on",
  "cross-referencing historical gossip about",
  "digging through civic archives for",
  "highlighting suspiciously relevant trivia about",
  "comparing dusty summaries related to",
  "checking the strategic briefing on",
  "annotating public knowledge concerning",
];

const SPECIALS = [
  "The oracle is rotating the crystal cache one notch to the left.",
  "Civilization advisors are arguing over the optimal research tree.",
  "A Sim just waved at the progress bar and carried on.",
  "The llama has entered a productive, if judgmental, silence.",
  "Public facts and local inference are being introduced politely.",
  "Someone marked your request as both urgent and mystical.",
  "We found the right scroll, now we are pretending that was easy.",
  "This prophecy is currently in quality assurance.",
];

const TEMPLATES = [
  "{opener} {agent} {action}. {ending}",
  "{agent} are {action}. {ending}",
  "{opener} {agent} while we tune the oracle stack. {ending}",
  "{opener} {agent} for this turn-based prophecy. {ending}",
  "{agent} report they are {action}. {ending}",
  "{opener} public and local signals through the {agent}. {ending}",
];

function randomItem<T>(items: T[]): T {
  return items[Math.floor(Math.random() * items.length)];
}

function pushUnique(target: string[], value: string, seen: Set<string>) {
  if (!seen.has(value)) {
    seen.add(value);
    target.push(value);
  }
}

export function buildWaitingPhrases(topic?: string | null, publicTitle?: string | null): string[] {
  const phrases: string[] = [];
  const seen = new Set<string>();

  const targetSize = 2200;
  let attempts = 0;
  while (phrases.length < targetSize && attempts < 40000) {
    attempts += 1;

    const template = randomItem(TEMPLATES);
    const opener = randomItem(OPENERS);
    const agent = randomItem(AGENTS);
    const action = randomItem(ACTIONS);
    const ending = randomItem(ENDINGS);

    const candidate = template
      .replace("{opener}", opener)
      .replace("{agent}", agent)
      .replace("{action}", action)
      .replace("{ending}", ending);

    pushUnique(phrases, candidate, seen);
  }

  for (const special of SPECIALS) {
    pushUnique(phrases, special, seen);
  }

  const focus = publicTitle ?? topic;
  if (focus) {
    for (const agent of AGENTS) {
      for (const action of TOPIC_ACTIONS) {
        for (const ending of ENDINGS.slice(0, 8)) {
          pushUnique(phrases, `${agent} are ${action} ${focus}. ${ending}`, seen);
        }
      }
    }
  }

  return phrases;
}

export function pickRandomPhraseIndex(
  poolSize: number,
  previousIndex?: number,
  recentIndices: number[] = [],
): number {
  if (poolSize <= 1) return 0;
  const blocked = new Set(recentIndices);
  let next = Math.floor(Math.random() * poolSize);
  if (previousIndex !== undefined) blocked.add(previousIndex);

  let guard = 0;
  while (blocked.has(next) && guard < 80) {
    next = Math.floor(Math.random() * poolSize);
    guard += 1;
  }
  return next;
}



