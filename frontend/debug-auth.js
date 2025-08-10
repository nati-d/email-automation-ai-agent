// Debug script to check authentication state
// Run this in browser console to check auth status

console.log('🔍 Debugging Authentication State');
console.log('================================');

// Check localStorage
const userStr = localStorage.getItem('user');
console.log('1. User string from localStorage:', userStr);

if (userStr) {
  try {
    const user = JSON.parse(userStr);
    console.log('2. Parsed user object:', user);
    
    const sessionId = user.sessionId || user.session_id;
    console.log('3. Extracted sessionId:', sessionId);
    
    if (sessionId) {
      console.log('✅ SessionId found, testing API call...');
      
      // Test API call
      fetch('http://127.0.0.1:8000/api/drafts/', {
        headers: {
          'Authorization': `Bearer ${sessionId}`,
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        console.log('4. API Response status:', response.status);
        console.log('4. API Response headers:', [...response.headers.entries()]);
        return response.json();
      })
      .then(data => {
        console.log('5. API Response data:', data);
      })
      .catch(error => {
        console.error('❌ API call failed:', error);
      });
    } else {
      console.log('❌ No sessionId found in user object');
    }
  } catch (error) {
    console.error('❌ Failed to parse user object:', error);
  }
} else {
  console.log('❌ No user found in localStorage');
}

console.log('================================');
console.log('🔍 Debug complete');