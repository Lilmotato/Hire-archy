import Heading from "@/components/Heading/Heading";
import Link from "next/link";

export default function Home() {
  return (
    <div className="flex sm:min-h-[85.5vh] min-h-[85vh] flex-col items-center justify-center text-center px-2 sm:py-8 py-12">
      <Heading heading={"Hire-Archy"} fontSize={"700%"}/>
      <p className="mb-8 sm:text-lg max-w-[800px] text-muted-foreground">
        Welcome to Hire-archy: where AI helps you find work, not steal it. We make job matching so smooth, even your imposter syndrome will be impressed
      </p>
      <div className="flex flex-row items-center gap-5">
        <Link href={`/signup`}>SignUp</Link>
        <Link href="/signin">SignIn</Link>
      </div>
    </div>
  );
}