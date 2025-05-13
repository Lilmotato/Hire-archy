'use client';

import { useState } from 'react';
import styles from './ApplyButton.module.css';
import Cookies from 'js-cookie';

export default function ApplyButton({ jobId }) {
  const [status, setStatus] = useState('idle'); // idle | loading | success | error

  const handleApply = async () => {
    setStatus('loading');
    try {
      const token = Cookies.get('token');
      const res = await fetch(`http://localhost:8000/jobs/${jobId}/apply`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'accept': 'application/json',
        },
      });

      if (!res.ok) {
        throw new Error('Failed to apply');
      }

      setStatus('success');
    } catch (err) {
      console.error(err);
      setStatus('error');
    }
  };

  return (
    <>
      {status === 'success' ? (
        <p className={styles.success}>✅ Applied successfully!</p>
      ) : (
        <button
          onClick={handleApply}
          disabled={status === 'loading'}
          className={styles.button}
        >
          {status === 'loading' ? 'Applying...' : 'Apply to this Job'}
        </button>
      )}
      {status === 'error' && <p className={styles.error}>❌ Failed to apply.</p>}
    </>
  );
}
