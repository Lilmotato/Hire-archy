import CandidateFilter from "@/components/CandidateFilter/CandidateFilter";
import CardHolder from "@/components/CardHolder/CardHolder";
import Heading from "@/components/Heading/Heading";
import Wrapper from "@/components/Wrapper/Wrapper";
import Navbar from "@/components/Navbar/Navbar";
import { cookies } from 'next/headers';

async function fetchRecruiterJobs(token) {
    try {
        const response = await fetch('http://localhost:8000/jobs/recruiter', {
            method: 'GET',
            headers: {
                'accept': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch recruiter jobs: ${response.status}`);
        }

        const jobs = await response.json();
        return jobs;
    } catch (error) {
        console.error('Error fetching recruiter jobs:', error);
        return [];
    }
}

export default async function RecruiterHome() {
    const kokkie = await cookies();
    const token = kokkie.get('token')?.value;
    const recruiterJobsData = await fetchRecruiterJobs(token);
    return (
        <Wrapper>
            <Navbar navbarLinks={[{key: "New Job", value: "/newjob"}, {key: "Logout", value: "/logout"}]} />
            <Heading heading={"Active Jobs"} />
            <CandidateFilter />
            <CardHolder jobs={recruiterJobsData} />
        </Wrapper>
    );
}