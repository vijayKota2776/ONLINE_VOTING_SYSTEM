import strawberry
from typing import List
from datetime import datetime
import random
from app.database import get_session

# ══════════════════════════════════════════
# TYPES
# ══════════════════════════════════════════

@strawberry.type
class ElectionType:
    id: int
    name: str
    start_date: str
    end_date: str
    status: str

@strawberry.type
class CandidateType:
    id: int
    name: str
    party: str

@strawberry.type
class VoterType:
    id: int
    name: str
    email: str
    voter_id_number: str
    has_voted: bool

@strawberry.type
class BallotType:
    id: int
    voted_at: str

@strawberry.type
class ResultType:
    id: int
    total_votes: int
    candidate: CandidateType # Changed to match your query: candidate { name }

# Response Wrappers for your specific query style
@strawberry.type
class CastVoteResponse:
    ballot: BallotType

@strawberry.type
class CloseElectionResponse:
    election: ElectionType

# ══════════════════════════════════════════
# INPUT
# ══════════════════════════════════════════

@strawberry.input
class CastVoteInput:
    election_id: int
    voter_id: int
    candidate_id: int

# ══════════════════════════════════════════
# QUERY
# ══════════════════════════════════════════

@strawberry.type
class Query:
    @strawberry.field
    def active_elections(self) -> List[ElectionType]:
        session = get_session()
        result = session.run("MATCH (e:Election {status: 'active'}) RETURN e")
        elections = [ElectionType(**record['e']) for record in result]
        session.close()
        return elections

    @strawberry.field
    def results(self, election_id: int) -> List[ResultType]:
        session = get_session()
        result = session.run("""
            MATCH (r:Result)-[:IN_ELECTION]->(:Election {id: $election_id})
            MATCH (r)-[:FOR_CANDIDATE]->(c:Candidate)
            RETURN r, c
        """, election_id=election_id)
        res = [
            ResultType(
                id=record['r']['id'],
                total_votes=record['r']['total_votes'],
                candidate=CandidateType(**record['c'])
            ) for record in result
        ]
        session.close()
        return res

# ══════════════════════════════════════════
# MUTATIONS
# ══════════════════════════════════════════

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_election(self, id: int, name: str, start_date: str, end_date: str) -> ElectionType:
        session = get_session()
        result = session.run("""
            MERGE (e:Election {id: $id})
            SET e.name = $name, e.start_date = $start_date, 
                e.end_date = $end_date, e.status = 'active'
            RETURN e
        """, id=id, name=name, start_date=start_date, end_date=end_date)
        e = result.single()['e']
        session.close()
        return ElectionType(**e)

    @strawberry.mutation
    def create_candidate(self, id: int, election_id: int, name: str, party: str) -> CandidateType:
        session = get_session()
        result = session.run("""
            MATCH (e:Election {id: $election_id})
            MERGE (c:Candidate {id: $id})
            SET c.name = $name, c.party = $party
            MERGE (c)-[:BELONGS_TO]->(e)
            RETURN c
        """, election_id=election_id, id=id, name=name, party=party)
        c = result.single()['c']
        session.close()
        return CandidateType(**c)

    @strawberry.mutation
    def register_voter(self, id: int, name: str, email: str, voter_id_number: str) -> VoterType:
        session = get_session()
        result = session.run("""
            MERGE (v:Voter {id: $id})
            SET v.name = $name, v.email = $email, 
                v.voter_id_number = $voter_id_number, v.has_voted = false
            RETURN v
        """, id=id, name=name, email=email, voter_id_number=voter_id_number)
        v = result.single()['v']
        session.close()
        return VoterType(**v)

    @strawberry.mutation
    def cast_vote(self, input: CastVoteInput) -> CastVoteResponse:
        session = get_session()
        
        election = session.run("MATCH (e:Election {id: $id}) RETURN e", id=input.election_id).single()
        if not election or election['e']['status'] != 'active':
            session.close()
            raise Exception("Election not active or not found!")

        voter = session.run("MATCH (v:Voter {id: $id}) RETURN v", id=input.voter_id).single()
        if not voter or voter['v']['has_voted']:
            session.close()
            raise Exception("Voter not found or already voted!")

        # Using toInteger(rand()) to avoid 'randomInteger' error
        result = session.run("""
            MATCH (v:Voter {id: $voter_id}), (c:Candidate {id: $candidate_id}), (e:Election {id: $election_id})
            CREATE (b:Ballot {id: toInteger(rand()*1000000), voted_at: $voted_at})
            CREATE (v)-[:CAST]->(b)-[:FOR]->(c), (b)-[:IN]->(e)
            SET v.has_voted = true
            RETURN b
        """, voter_id=input.voter_id, candidate_id=input.candidate_id, 
             election_id=input.election_id, voted_at=datetime.utcnow().isoformat())
        
        b = result.single()['b']
        session.close()
        return CastVoteResponse(ballot=BallotType(id=b['id'], voted_at=b['voted_at']))

    @strawberry.mutation
    def close_election(self, id: int) -> CloseElectionResponse:
        session = get_session()
        session.run("""
            MATCH (e:Election {id: $id})
            SET e.status = 'closed'
            WITH e
            MATCH (c:Candidate)-[:BELONGS_TO]->(e)
            OPTIONAL MATCH (b:Ballot)-[:FOR]->(c)
            WITH e, c, count(b) AS total
            CREATE (r:Result {id: toInteger(rand()*1000000), total_votes: total})
            CREATE (r)-[:FOR_CANDIDATE]->(c), (r)-[:IN_ELECTION]->(e)
        """, id=id)
        res = session.run("MATCH (e:Election {id: $id}) RETURN e", id=id).single()
        e = res['e']
        session.close()
        return CloseElectionResponse(election=ElectionType(**e))

schema = strawberry.Schema(query=Query, mutation=Mutation)
