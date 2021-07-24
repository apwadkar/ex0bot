import { expect, haveResource } from "@aws-cdk/assert";
import { App } from "@serverless-stack/resources";
import Ex0botStack from "../lib/Ex0botStack";

test("Test Stack", () => {
  const app = new App();
  // WHEN
  const stack = new Ex0botStack(app, "test-stack");
  // THEN
  expect(stack).to(haveResource("AWS::Lambda::Function"));
});
