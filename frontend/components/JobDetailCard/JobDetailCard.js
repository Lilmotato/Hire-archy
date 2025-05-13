'use client';
import React from "react";
import ApplyButton from "../ApplyButton/ApplyButton";
import styles from "./JobDetailCard.module.css";
import Cookies from 'js-cookie';

async function applyToJob(token, jobId) {
  try {
    const response = await fetch(`http://localhost:8000/jobs/${jobId}/apply`, {
      method: 'POST',
      headers: {
        'accept': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: null
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const result = await response.json();
    console.log('Application response:', result);
    return result;
  } catch (error) {
    console.error('Error applying to job:', error);
    return null;
  }
}

export default function JobDetailCard({
  role,
  jobId,
  jobTitle,
  jobDescription,
  location,
  experience,
  keySkills = [],
  companyName,
}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const handleApply = async () => {
    const token = Cookies.get('token');
    if (!token) {
      console.warn("No token found. User must be logged in.");
      return;
    }
    await applyToJob(token, jobId);
  };

  return (
    <section className={styles.main}>
      <div className={`${styles.container} ${styles.wrapper}`}>
        <div className={styles.card}>
          <h2 className={styles.title}>{jobTitle}</h2>
          <p className={styles.company}>Company: {companyName}</p>
          <p className={styles.description}>{jobDescription}</p>
          <p>
            <strong>Location:</strong> {location}
          </p>
          <p>
            <strong>Experience:</strong> {experience} years
          </p>

          <div className={styles.skills}>
            {keySkills.map((skill, idx) => (
              <span key={idx} className={styles.skill}>
                {skill}
              </span>
            ))}
          </div>

          {/* {role === "candidate" && (
            <div className={styles.buttonContainer}>
              <button className={styles.applyButton} onClick={handleApply}>
                Apply Now
              </button>
            </div>
          )} */}

          {role === "candidate" && <ApplyButton jobId={jobId} />}

        </div>
      </div>
    </section>
  );
}
