# Nodes:
#   (:Election {id, name, start_date, end_date, status})
#   (:Candidate {id, name, party})
#   (:Voter {id, name, email, voter_id_number, has_voted})
#   (:Ballot {id, voted_at})
#   (:Result {id, total_votes})

# Relationships:
#   (:Candidate)-[:BELONGS_TO]->(:Election)
#   (:Voter)-[:CAST]->(:Ballot)
#   (:Ballot)-[:FOR]->(:Candidate)
#   (:Ballot)-[:IN]->(:Election)
#   (:Result)-[:FOR_CANDIDATE]->(:Candidate)
#   (:Result)-[:IN_ELECTION]->(:Election)