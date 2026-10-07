\# Week 21 Day 5 — Architecture v2 Integration Testing



\## Objective



Prove that Architecture v2 retrieval integrates safely with the existing governance and assurance layer.



The central question was:



> Can Architecture v2 improve or recover evidence without bypassing the safety controls built during Weeks 18–20?



\---



\## Architecture Tested



```text

Question

&#x20;  |

&#x20;  v

Scope Gate

&#x20;  |

&#x20;  v

Initial Hybrid Retrieval

&#x20;  |

&#x20;  v

Evidence Sufficiency

&#x20;  |

&#x20;  v

Deterministic Retrieval Router

&#x20;  |

&#x20;  +---- RETURN\_INITIAL

&#x20;  |

&#x20;  +---- RELATIONSHIP\_AWARE

&#x20;  |

&#x20;  +---- BOUNDED\_AGENTIC

&#x20;  |

&#x20;  +---- HYBRID\_RESCUE

&#x20;  |

&#x20;  +---- STOP\_INSUFFICIENT

&#x20;  |

&#x20;  v

Final Evidence Assessment

&#x20;  |

&#x20;  v

Retrieval-to-Governance Integration Gate

&#x20;  |

&#x20;  v

Existing Pre-Generation Governance

&#x20;  |

&#x20;  +---- AUTO\_ANSWER

&#x20;  +---- REVIEW\_REQUIRED

&#x20;  +---- ABSTAIN

&#x20;  |

&#x20;  v

Answer Generation

&#x20;  |

&#x20;  v

Citation Verification

&#x20;  |

&#x20;  v

Existing Post-Generation Governance

&#x20;  |

&#x20;  +---- AUTO\_ANSWER

&#x20;  +---- REVIEW\_REQUIRED

&#x20;  +---- ABSTAIN

