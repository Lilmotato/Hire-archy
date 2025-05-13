import SigninForm from "@/components/SignInForm/SignInForm";
import Wrapper from "@/components/Wrapper/Wrapper";
import Navbar from "@/components/Navbar/Navbar";

export default function SignInPage() {
    return (
        <Wrapper>
            <Navbar navbarLinks={[{key: "SignUp", value: "/signup"}]} />
            <SigninForm />
        </Wrapper>
    )
}