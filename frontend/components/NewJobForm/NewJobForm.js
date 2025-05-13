'use client';

import { useState, useEffect } from 'react';
import styles from "./NewJobForm.module.css";
import Heading from "../Heading/Heading";
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import { decodeJwtRole } from '@/utils/auth';
import Unauthorized from '../Unauthorized/Unauthorized';
import Loading from '../Loading/Loading';

export default function NewJobForm() {
  const [role, setRole] = useState(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [keySkills, setKeySkills] = useState('');
  const [experience, setExperience] = useState('');
  const [location, setLocation] = useState('');
  const [company, setCompany] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const router = useRouter();

  // ✅ Check role on mount
  useEffect(() => {
    const token = Cookies.get('token');
    if (!token) return;

    const decodedRole = decodeJwtRole(token);
    setRole(decodedRole);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    try {
      const token = Cookies.get('token');
      if (!token) throw new Error("Not authenticated");

      const res = await fetch('http://localhost:8000/jobs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'accept': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          title,
          description,
          key_skills: keySkills.split(',').map(s => s.trim()).filter(Boolean),
          experience_required: parseInt(experience),
          location,
          company_name: company,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Job creation failed');
      }

      const job = await res.json();
      console.log('Job created:', job);
      router.push('/recruiterhome');
    } catch (err) {
      console.error('Job creation error:', err);
      setErrorMsg(err.message);
    }
  };

  if (role === null) {
    return <Loading />;
  }

  if (role !== 'recruiter') {
    return (
      <Unauthorized />
    );
  }

  // ✅ Recruiter-only form
  return (
    <main className={styles.main}>
      <div className={`${styles.container} ${styles.wrapper}`}>
        <div className={styles.formSection}>
          <Heading heading={"Post a New Job"} />
          <form className={styles.form} onSubmit={handleSubmit}>
            <input
              type="text"
              placeholder="Job Title"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            <textarea
              placeholder="Job Description"
              required
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            <input
              type="text"
              placeholder="Key Skills (comma separated)"
              required
              value={keySkills}
              onChange={(e) => setKeySkills(e.target.value)}
            />
            <input
              type="number"
              placeholder="Experience Required (years)"
              required
              min="0"
              value={experience}
              onChange={(e) => setExperience(e.target.value)}
            />
            <input
              type="text"
              placeholder="Location"
              required
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
            <input
              type="text"
              placeholder="Company Name"
              required
              value={company}
              onChange={(e) => setCompany(e.target.value)}
            />
            {errorMsg && <p className={styles.error}>{errorMsg}</p>}
            <button type="submit">Create Job</button>
          </form>
        </div>
        <div className={styles.imageSection}>
          <img
            src="https://firebase.google.com/static/images/brand-guidelines/logo-vertical.png"
            alt="New Job Visual"
          />
        </div>
      </div>
    </main>
  );
}
