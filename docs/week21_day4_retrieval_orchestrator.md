\# Week 21 Day 4 — Deterministic Retrieval Orchestrator



\## Objective



Build a clean Architecture v2 retrieval controller that decides which retrieval capability should run after the initial Hybrid search.



The key design question was:



> Given a question and initial Hybrid evidence, which retrieval capability should run next — if any?



The orchestrator must remain deterministic, bounded, auditable, and governance-first.



\---



\## Architecture Principle



Architecture v2 follows:



\*\*Simplify the intelligence layer, preserve the assurance layer.\*\*



The orchestrator does not give an unrestricted AI agent freedom to select arbitrary tools.



Instead, it uses deterministic routing rules over:



\- query scope

\- initial Hybrid evidence

\- evidence sufficiency

\- unsupported claim types

\- missing evidence topics

\- verified document relationships



The orchestrator may execute at most one retrieval enhancement route.



\---



\## Retrieval Flow



```text

Question

&#x20;  |

&#x20;  v

Scope Gate

&#x20;  |

&#x20;  +---- OUT OF SCOPE ----> STOP

&#x20;  |

&#x20;  v

Initial Hybrid Retrieval

&#x20;  |

&#x20;  v

Evidence Sufficiency Assessment

&#x20;  |

&#x20;  v

Deterministic Retrieval Diagnosis

&#x20;  |

&#x20;  +---- sufficient evidence

&#x20;  |         |

&#x20;  |         v

&#x20;  |    RETURN\_INITIAL

&#x20;  |

&#x20;  +---- hard-blocked unsupported claim

&#x20;  |         |

&#x20;  |         v

&#x20;  |    STOP\_INSUFFICIENT

&#x20;  |

&#x20;  +---- unsupported relationship claim

&#x20;  |     + verified registry relationship

&#x20;  |         |

&#x20;  |         v

&#x20;  |    RELATIONSHIP\_AWARE

&#x20;  |

&#x20;  +---- recoverable controlled missing topic

&#x20;  |         |

&#x20;  |         v

&#x20;  |    BOUNDED\_AGENTIC

&#x20;  |

&#x20;  +---- same-query evidence gap

&#x20;            |

&#x20;            v

&#x20;       HYBRID\_RESCUE

