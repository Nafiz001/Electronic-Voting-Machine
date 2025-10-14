// Test Firebase connection
import firebaseService from './src/services/firebase.js';

// Test the Firebase service
async function testFirebaseConnection() {
  console.log('Testing Firebase connection...');
  
  try {
    // Test getting voters
    console.log('\n1. Testing getVoters():');
    const voters = await firebaseService.getVoters();
    console.log('Voters:', voters);
    
    // Test getting votes
    console.log('\n2. Testing getVotes():');
    const votes = await firebaseService.getVotes();
    console.log('Votes:', votes);
    
    // Test getting voters with status
    console.log('\n3. Testing getVotersWithStatus():');
    const votersWithStatus = await firebaseService.getVotersWithStatus();
    console.log('Voters with status:', votersWithStatus);
    
    // Test getting vote counts
    console.log('\n4. Testing getVoteCounts():');
    const voteCounts = await firebaseService.getVoteCounts();
    console.log('Vote counts:', voteCounts);
    
    // Test getting dashboard stats
    console.log('\n5. Testing getDashboardStats():');
    const dashboardStats = await firebaseService.getDashboardStats();
    console.log('Dashboard stats:', dashboardStats);
    
    console.log('\n✅ All Firebase tests completed successfully!');
  } catch (error) {
    console.error('❌ Error testing Firebase connection:', error);
  }
}

// Run the test
testFirebaseConnection();