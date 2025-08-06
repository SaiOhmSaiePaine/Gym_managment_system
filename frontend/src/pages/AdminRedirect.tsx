import React from 'react';

const AdminRedirect = () => {
  console.log('AdminRedirect component rendered');
  return (
    <div style={{ 
      padding: '40px', 
      textAlign: 'center',
      background: '#f3f4f6',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center'
    }} id="admin-redirect-component">
      <h2 style={{ color: '#1f2937', marginBottom: '16px' }}>🔒 Admin Access Moved</h2>
      <p style={{ color: '#6b7280', marginBottom: '24px' }}>The admin interface is now available at:</p>
      <a 
        href="http://localhost:8000/admin" 
        style={{
          display: 'inline-block',
          padding: '12px 24px',
          background: '#3b82f6',
          color: 'white',
          textDecoration: 'none',
          borderRadius: '8px',
          fontSize: '16px',
          fontWeight: '500'
        }}
      >
        Go to Admin Interface →
      </a>
      <p style={{ color: '#9ca3af', marginTop: '16px', fontSize: '14px' }}>
        Credentials: admin / admin123
      </p>
    </div>
  );
};

export default AdminRedirect;
