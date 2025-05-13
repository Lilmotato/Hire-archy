'use client';

import { useState } from 'react';
import styles from './ProfileForm.module.css';
import Heading from '../Heading/Heading';
import { updateProfile } from '@/app/actions/updateProfile';
import Cookies from 'js-cookie';
import { useRouter } from 'next/navigation';
import Loading from '../Loading/Loading';

export default function ProfileForm() {
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(false);
  const [profileUpdated, setProfileUpdated] = useState(false); // ✅ success message state
  const [profileLoading, setProfileLoading] = useState(false); // ✅ new state
  const router = useRouter();

  const handleResumeUpload = async (e) => {
    e.preventDefault();
    if (!resume) return;

    const token = Cookies.get('token');
    if (!token) {
      console.error('No auth token found');
      return;
    }

    const formData = new FormData();
    formData.append('file', resume);

    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/resume', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const data = await response.json();
      console.log('Resume uploaded:', data);

      router.push('/userhome');
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload resume');
    } finally {
      setLoading(false);
    }
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setProfileLoading(true);
    const formData = new FormData(e.target);

    const body = {
      full_name: formData.get('full_name')?.trim() || '',
      phone_number: formData.get('phone_number')?.trim() || '',
      location: formData.get('location')?.trim() || '',
      years_of_experience: parseInt(formData.get('years_of_experience') || '0', 10),
      key_skills: formData.get('key_skills')
        ?.split(',')
        .map(s => s.trim())
        .filter(Boolean) || [],
    };

    try {
      const normalizedFormData = new FormData();
      normalizedFormData.append('full_name', body.full_name);
      normalizedFormData.append('phone_number', body.phone_number);
      normalizedFormData.append('location', body.location);
      normalizedFormData.append('years_of_experience', body.years_of_experience);
      normalizedFormData.append('key_skills', body.key_skills.join(','));

      await updateProfile(normalizedFormData);
      setProfileUpdated(true);
    } catch (err) {
      console.error('Error updating profile:', err);
      setProfileUpdated(false);
    } finally {
      setProfileLoading(false);
    }
  };



  if (loading) return <Loading />;

  return (
    <section className={styles.main}>
      <div className={`${styles.container} ${styles.wrapper}`}>
        {/* === Resume Upload Form === */}
        <form className={styles.form} onSubmit={handleResumeUpload}>
          <Heading heading={"Upload Resume"} />
          <input
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={(e) => setResume(e.target.files[0])}
            required
          />
          <button type="submit">Upload Resume</button>
        </form>

        {/* === Profile Details Form === */}
        <form className={styles.form} onSubmit={handleProfileUpdate}>
          <Heading heading={"Profile Details"} />
          <input name="full_name" type="text" placeholder="Full Name" />
          <input name="phone_number" type="tel" placeholder="Phone Number" />
          <input name="location" type="text" placeholder="Location" />
          <input name="years_of_experience" type="number" placeholder="Years of Experience" min="0" />
          <input name="key_skills" type="text" placeholder="Key Skills (comma separated)" />
          <button type="submit" disabled={profileLoading}>
            {profileLoading ? 'Updating...' : 'Save Profile'}
          </button>
          {profileUpdated && (
            <p style={{ color: 'green', marginTop: '0.75rem' }}>
              ✅ Profile updated successfully!
            </p>
          )}
        </form>

      </div>
    </section>
  );
}
