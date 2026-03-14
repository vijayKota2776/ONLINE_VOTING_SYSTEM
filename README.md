# 🗳️ ONLINE VOTING SYSTEM (GraphQL + Neo4j)

**GitHub Repository:** https://github.com

A modern, high-integrity voting API built with **Python**, **Strawberry GraphQL**, and **Neo4j**. This system leverages graph relationships to enforce voting rules and provides a seamless single-endpoint experience for managing elections from start to finish.

---

## 🚀 Key Features

- **Graph-Based Integrity:** Uses Neo4j relationships to prevent double-voting and ensure ballot authenticity.
- **Flexible API:** Single `/graphql` endpoint allowing clients to fetch exactly the data they need.
- **Automated Results:** An atomic calculation process that triggers upon closing an election.
- **Robust Validation:** Real-time checks for voter eligibility, election status, and duplicate entries.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|------|-------------|---------|
| **Backend** | Python (FastAPI + Strawberry) | Core business logic and GraphQL API |
| **API Protocol** | GraphQL | Optimized data fetching and mutations |
| **Database** | Neo4j 5.x | Graph database for voter/election relationships |
| **Server** | Uvicorn | High-performance ASGI web server |

---

## 📂 Project Structure

```text
ONLINE_VOTING_SYSTEM/
│
├── main.py
│
├── app/
│   └── database.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

**File Description**

- `main.py` → Entry point containing GraphQL types, queries, and mutations  
- `app/database.py` → Neo4j driver connection and session management  
- `.env` → Environment variables for database credentials  
- `.gitignore` → Files to ignore in Git commits  
- `requirements.txt` → Python dependencies  
- `README.md` → Project documentation  

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com
cd ONLINE_VOTING_SYSTEM
```

---

### 2️⃣ Configure Environment Variables

Create a `.env` file in the root folder:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Run the API

```bash
uvicorn main:app --reload
```

The interactive **GraphQL playground** will be available at:

```
http://localhost:8000/graphql
```

---

## 🧪 Testing the Workflow (GraphQL Queries)

### Step 1️⃣ Initialize System

Run this mutation to set up an election, a candidate, and a voter.

```graphql
mutation Setup {
  createElection(
    id: 1
    name: "2024 Presidential Election"
    startDate: "2024-01-01"
    endDate: "2024-12-31"
  ) {
    id
    status
  }

  createCandidate(
    id: 10
    electionId: 1
    name: "Alice Blue"
    party: "Tech Party"
  ) {
    id
  }

  registerVoter(
    id: 99
    name: "Vijay Kota"
    email: "vijay@test.com"
    voterIdNumber: "V74"
  ) {
    id
  }
}
```

---

### Step 2️⃣ Cast a Ballot

```graphql
mutation Vote {
  castVote(
    input: {
      electionId: 1
      voterId: 99
      candidateId: 10
    }
  ) {
    ballot {
      id
      votedAt
    }
  }
}
```

---

### Step 3️⃣ Finalize Election & View Results

```graphql
mutation Close {
  closeElection(id: 1) {
    election {
      status
    }
  }
}

query ViewResults {
  results(electionId: 1) {
    totalVotes
    candidate {
      name
      party
    }
  }
}
```

---

## 🛡️ Business Rules

1. **Voter Verification** – Only registered users can cast votes.  
2. **No Double Voting** – The system returns an error if a voter attempts a second ballot.  
3. **Time Locking** – Votes can only be cast when the election status is **active**.  
4. **Atomic Tally** – Closing an election triggers a graph traversal ensuring every ballot is counted exactly once.

---

## 👤 Author Information

**Primary Author:** Vijay Kota  
**Collaborator:** Mark Zuckerberg  
**Roll Number:** 150096724074

---

## 💡 Pro Tip (Fix README Not Showing on GitHub)

If your `README.md` exists but GitHub is not displaying it, try renaming and pushing again:

```bash
git mv README.md README.temp
git mv README.temp README.md
git commit -m "Fixing README display"
git push
```

This forces Git to refresh the file in the repository.

---