import CandidateCard from "@/components/CandidateCard/CandidateCard";
import Heading from "@/components/Heading/Heading";
import Navbar from "@/components/Navbar/Navbar";
import JobDetailCard from "@/components/JobDetailCard/JobDetailCard";
import Wrapper from "@/components/Wrapper/Wrapper";
import { cookies } from 'next/headers';
import { decodeJwtRole } from "@/utils/auth";

async function fetchJobDetail(jobId, token = null) {
    try {
        const kokkie = await cookies();
        const token = kokkie.get('token')?.value;

        const headers = {
            'accept': 'application/json',
        };

        if (!token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`http://localhost:8000/jobs/${jobId}`, {
            method: 'GET',
            headers: headers,
            cache: 'no-store',
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch job ${jobId}: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching job detail:', error);
        return null;
    }
}

async function fetchRankedCandidates(jobId, token) {
    try {
        const response = await fetch(`http://localhost:8000/ranked-candidates?job_id=${jobId}`, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch ranked candidates: ${response.status}`);
        }

        const candidates = await response.json();
        return candidates;
    } catch (error) {
        console.error('Error fetching ranked candidates:', error);
        return [];
    }
}

export default async function JobPage({ params }) {
    const prms = await params
    const jobId = prms.slug;
    const jobDetailData = await fetchJobDetail(jobId);
    const kokkie = await cookies();
    const token = kokkie.get('token')?.value;
    const role = decodeJwtRole(token)
    let navbarLinks = [{key: "Candidate Home", value: "/userhome"}, {key: "Logout", value: "/logout"}]
    let rankedCandidatesData = null;
    if (role == "recruiter") {
        navbarLinks = [{key: "Recruiter Home", value: "/recruiterhome"}, {key: "New Job", value: "/newjob"}, {key: "Logout", value: "/logout"}]
        rankedCandidatesData = await fetchRankedCandidates(jobId, token)
    }

    if (!jobDetailData) {
        return <p>Job not found or error fetching data.</p>;
    }

    return (
        <Wrapper>
            <Navbar navbarLinks={navbarLinks} />
            <JobDetailCard role={role} jobId={jobId} jobTitle={jobDetailData.title} jobDescription={jobDetailData.description} location={jobDetailData.location} experience={jobDetailData.experience_required} keySkills={jobDetailData.key_skills} companyName={jobDetailData.company_name} />
            {rankedCandidatesData != null ? <div><Heading heading={"Candidates applied to this job"} />
                {rankedCandidatesData.candidates.map((candidate, idx) => (
                    <CandidateCard
                        key={idx}
                        name={candidate.full_name}
                        email={candidate.email}
                        resumeLink={candidate.resume_url}
                        keySkills={candidate.key_skills}
                        location={candidate.location}
                        experience={candidate.years_of_experience}
                        score={candidate.score}
                        phoneNumber={candidate.phone_number}

                    />
                ))}</div> : ""}
        </Wrapper>
    );
}
