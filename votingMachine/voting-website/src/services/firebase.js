// Firebase Realtime Database service using REST API
const FIREBASE_URL = 'https://e-vm-f7bdf-default-rtdb.firebaseio.com';

class FirebaseService {
  // Get all voters
  async getVoters() {
    try {
      const response = await fetch(`${FIREBASE_URL}/voters.json`);
      if (!response.ok) {
        throw new Error('Failed to fetch voters');
      }
      const data = await response.json();
      
      if (!data) return [];
      
      // Handle both array and object formats
      if (Array.isArray(data)) {
        // Firebase returns array, filter out null values and map with index as ID
        return data
          .map((voter, index) => voter ? {
            id: index.toString(),
            name: voter.name,
            hasVoted: false, // Will be determined by checking votes
            votedAt: null
          } : null)
          .filter(Boolean); // Remove null entries
      } else {
        // Firebase returns object, convert to array
        return Object.entries(data).map(([id, voter]) => ({
          id,
          name: voter.name,
          hasVoted: false, // Will be determined by checking votes
          votedAt: null
        }));
      }
    } catch (error) {
      console.error('Error fetching voters:', error);
      return [];
    }
  }

  // Get all votes
  async getVotes() {
    try {
      const response = await fetch(`${FIREBASE_URL}/votes.json`);
      if (!response.ok) {
        throw new Error('Failed to fetch votes');
      }
      const data = await response.json();
      
      if (!data) return [];
      
      // Convert Firebase object to array
      return Object.entries(data).map(([id, vote]) => ({
        id,
        candidate: vote.candidate,
        timestamp: vote.timestamp,
        voter_id: vote.voter_id
      }));
    } catch (error) {
      console.error('Error fetching votes:', error);
      return [];
    }
  }

  // Get combined voter data with vote status
  async getVotersWithStatus() {
    try {
      const [voters, votes] = await Promise.all([
        this.getVoters(),
        this.getVotes()
      ]);

      // Create a map of voted voter IDs with their vote details
      const votedVoters = new Map();
      votes.forEach(vote => {
        votedVoters.set(vote.voter_id, {
          votedAt: new Date(vote.timestamp).toLocaleTimeString(),
          candidate: vote.candidate
        });
      });

      // Update voters with voting status
      return voters.map(voter => {
        const voteInfo = votedVoters.get(voter.id);
        return {
          ...voter,
          hasVoted: !!voteInfo,
          votedAt: voteInfo?.votedAt || null,
          votedFor: voteInfo?.candidate || null
        };
      });
    } catch (error) {
      console.error('Error fetching voters with status:', error);
      return [];
    }
  }

  // Get vote counts for each candidate
  async getVoteCounts() {
    try {
      const votes = await this.getVotes();
      const candidates = ['Alice', 'Bob', 'Charlie'];
      
      // Count votes for each candidate
      const voteCounts = candidates.map(candidate => {
        const candidateVotes = votes.filter(vote => vote.candidate === candidate);
        return {
          name: candidate,
          votes: candidateVotes.length,
          voters: candidateVotes.map(vote => vote.voter_id)
        };
      });

      // Calculate percentages
      const totalVotes = votes.length;
      return voteCounts.map(candidate => ({
        ...candidate,
        percentage: totalVotes > 0 ? (candidate.votes / totalVotes) * 100 : 0
      })).sort((a, b) => b.votes - a.votes); // Sort by votes descending
    } catch (error) {
      console.error('Error fetching vote counts:', error);
      return [];
    }
  }

  // Get dashboard statistics
  async getDashboardStats() {
    try {
      const [voters, votes] = await Promise.all([
        this.getVoters(),
        this.getVotes()
      ]);

      console.log('Dashboard stats - Voters:', voters);
      console.log('Dashboard stats - Votes:', votes);

      const totalVoters = voters.length;
      const totalVotes = votes.length;
      const candidates = 3; // Alice, Bob, Charlie
      const turnoutRate = totalVoters > 0 ? (totalVotes / totalVoters) * 100 : 0;

      const stats = {
        totalVoters,
        totalVotes,
        candidates,
        turnoutRate: turnoutRate.toFixed(1)
      };

      console.log('Final dashboard stats:', stats);
      return stats;
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      return {
        totalVoters: 0,
        totalVotes: 0,
        candidates: 3,
        turnoutRate: '0.0'
      };
    }
  }
}

export default new FirebaseService();